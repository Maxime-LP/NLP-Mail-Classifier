from sklearn.pipeline import Pipeline
from melusine.utils.transformer_scheduler import TransformerScheduler
from melusine.prepare_email.manage_transfer_reply import check_mail_begin_by_transfer, update_info_for_transfer_mail, add_boolean_transfer, add_boolean_answer
from melusine.prepare_email.build_historic import build_historic
from melusine.prepare_email.mail_segmenting import structure_email
from melusine.prepare_email.body_header_extraction import extract_last_body
from melusine.prepare_email.cleaning import clean_body


def preprocessing_melusine_df(df):

    ManageTransferReply = TransformerScheduler(
    functions_scheduler=[
        (check_mail_begin_by_transfer, None, ['is_begin_by_transfer']),
        (update_info_for_transfer_mail, None, None),
        (add_boolean_answer, None, ['is_answer']),
        (add_boolean_transfer, None, ['is_transfer'])
    ])

    EmailSegmenting = TransformerScheduler(
    functions_scheduler=[
        (build_historic, None, ['structured_historic']),
        (structure_email, None, ['structured_body'])
    ])

    Cleaning = TransformerScheduler(
    functions_scheduler=[
        (extract_last_body, None, ['last_body']),
        (clean_body, None, ['clean_body'])
    ])

    prepare_data_pipeline = Pipeline([
    ('ManageTransferReply', ManageTransferReply),
    ('EmailSegmenting', EmailSegmenting),
    ('Cleaning', Cleaning),
    ])

    df = prepare_data_pipeline.fit_transform(df)
    return df