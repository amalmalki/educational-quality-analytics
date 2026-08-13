"""اختبارات انحدار لمنطق منصة تحليلات الجودة التعليمية."""

import ast
import io
from pathlib import Path

import numpy as np
import pandas as pd


APP_PATH = Path(__file__).with_name("app(1).py")


def load_logic_namespace():
    tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
    body = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            node.names = [
                item for item in node.names
                if not item.name.startswith("streamlit")
            ]
            if node.names:
                body.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            body.append(node)
        elif isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if names and all(name.isupper() for name in names):
                body.append(node)

    namespace = {}
    module = ast.Module(body=body, type_ignores=[])
    exec(compile(module, str(APP_PATH), "exec"), namespace)
    return namespace


NS = load_logic_namespace()


class Upload(io.BytesIO):
    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name
        self.size = len(data)


def test_individual_responses_win_over_generic_aggregate_words():
    base = {
        "q1": [1, 2, 3, 4, 5, 3, 4, 2],
        "q2": [2, 3, 4, 5, 4, 3, 2, 1],
    }
    for extra in [
        "satisfaction_rate",
        "frequency_of_use",
        "completion_percentage",
        "average_time",
    ]:
        frame = pd.DataFrame({**base, extra: [1, 2, 3, 4, 5, 3, 4, 2]})
        assert NS["detect_dataset_type"](frame)[0] == "respondent_level"


def test_real_aggregate_and_frequency_shapes_are_still_detected():
    aggregate = pd.DataFrame(
        {
            "question": ["q1", "q2", "q3"],
            "mean": [4.1, 3.8, 4.4],
            "percentage": [82, 76, 88],
        }
    )
    frequency = pd.DataFrame(
        {
            "question": ["q1", "q2", "q3"],
            "strongly agree": [10, 11, 12],
            "agree": [20, 18, 22],
            "neutral": [3, 5, 2],
        }
    )
    assert NS["detect_dataset_type"](aggregate)[0] == "aggregated"
    assert NS["detect_dataset_type"](frequency)[0] == "frequency_distribution"


def test_ambiguous_observed_values_do_not_claim_wrong_scale():
    frame = pd.DataFrame({"q1": [2, 3, 4], "q2": [3, 4, 2]})
    assert NS["infer_scale"](frame, ["q1", "q2"]) == (1.0, 5.0, 0.35)


def test_out_of_range_values_are_removed_from_every_calculation():
    frame = pd.DataFrame({"q1": [5, 4, 99], "q2": [5, 4, 3]})
    cleaned, excluded = NS["exclude_out_of_range_values"](frame, frame.columns, 1, 5)
    assert excluded == {"q1": 1}
    assert pd.isna(cleaned.loc[2, "q1"])
    descriptive = NS["build_descriptive"](cleaned, list(cleaned.columns))
    overall = NS["equal_weight_item_mean"](descriptive)
    satisfaction = np.clip((overall - 1) / 4 * 100, 0, 100)
    assert 0 <= satisfaction <= 100
    assert satisfaction == 81.25


def test_equal_item_weighting_is_not_cell_weighting():
    frame = pd.DataFrame({"q1": [5.0] * 100, "q2": [1.0] + [np.nan] * 99})
    descriptive = NS["build_descriptive"](frame, list(frame.columns))
    assert NS["equal_weight_item_mean"](descriptive) == 3.0


def test_identifier_variants_are_excluded():
    values = pd.Series([1, 2, 3, 4, 5])
    for name in [
        "student_id",
        "student_number",
        "employee_number",
        "serial_number",
        "code",
        "رقم الطالب",
        "الرقم الجامعي",
    ]:
        assert NS["looks_like_identifier"](name, values)
    assert not NS["looks_like_identifier"]("validity_score", values)


def test_numeric_normalization_and_infinities():
    values = NS["clean_numeric_series"](
        pd.Series(["1,000", "2,5", "١٬٢٥٠", "inf", "-inf"])
    )
    assert values.iloc[:3].tolist() == [1000.0, 2.5, 1250.0]
    assert values.iloc[3:].isna().all()


def test_total_cell_limit():
    frame = pd.DataFrame(np.ones((20_001, 500), dtype=np.int8))
    try:
        NS["enforce_dataframe_limits"](frame)
    except NS["UserInputError"] as exc:
        assert "خلية" in str(exc)
    else:
        raise AssertionError("جدول يتجاوز عشرة ملايين خلية لم يُرفض")


def test_fake_and_entity_files_are_rejected():
    for data, name in [
        (b"not pdf", "fake.pdf"),
        (b"PK\x03\x04junk", "fake.xlsx"),
        (
            b'<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><root>&e;</root>',
            "evil.xml",
        ),
    ]:
        try:
            NS["load_file"](Upload(data, name))
        except Exception:
            pass
        else:
            raise AssertionError(f"لم يُرفض الملف الخطر: {name}")


def test_excel_formula_injection_is_neutralized():
    frame = pd.DataFrame({"x": ["=1+1", "+cmd", "@formula", "normal"]})
    safe = NS["sanitize_dataframe_for_excel"](frame)
    assert all(value.startswith("'") for value in safe["x"].iloc[:3])
    assert safe["x"].iloc[3] == "normal"


if __name__ == "__main__":
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"RESULT {len(tests)}/{len(tests)} passed")
