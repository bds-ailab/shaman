"""
This file defines given body messages and expected response code and response message.
"""
parametrize_create_experiment = [
    "experiment,status_code,result",
    [
        # Valid example
        (
            {
                "experiment_id": "abcd",
                "jobids": [1, 2, 3],
                "experiment_name": "test_experiment",
            },
            202,
            {"id": "abcd"},
        ),
        # Missing experiment_id
        (
            {"jobids": [1, 2, 3], "experiment_name": "test_experiment"},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "experiment", "experiment_id"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        # Missing jobids
        (
            {"experiment_id": "abcd", "experiment_name": "test_experiment"},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "experiment", "jobids"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        # Missing experiment_name
        (
            {"experiment_id": "abcd", "jobids": [1, 2, 3]},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "experiment", "experiment_name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
    ],
]


parametrize_update_experiment = [
    "experiment_id,intermediate_result,status_code",
    [(1, {"perf": 12, "parameters": {"a": 1, "b": 2}}, 202)],
]


parametrize_close_experiment = [
    "experiment_id,final_result,status_code",
    [(1, {"best_perf": 12, "best_parameters": {"a": 1, "b": 2}}, 202)],
]
