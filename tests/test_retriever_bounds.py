from unittest.mock import MagicMock
from src.retriever import get_retriever

def test_retriever_top_k_parameter_propagation():
    mock_vs = MagicMock()
    mock_vs.as_retriever.return_value = MagicMock()

    retriever = get_retriever(mock_vs, top_k=7, search_type="similarity")
    assert retriever is not None
    mock_vs.as_retriever.assert_called_once_with(
        search_type="similarity",
        search_kwargs={"k": 7}
    )

def test_retriever_mmr_parameter_propagation():
    mock_vs = MagicMock()
    mock_vs.as_retriever.return_value = MagicMock()

    retriever = get_retriever(mock_vs, top_k=5, search_type="mmr")
    assert retriever is not None
    mock_vs.as_retriever.assert_called_once_with(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 15}
    )
