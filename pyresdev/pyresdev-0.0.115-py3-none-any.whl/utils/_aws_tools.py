

__all__ = ['save_df_for_s3']

import logging
logger = logging.getLogger(__name__)


def save_df_for_s3(df,path,dataset_type,keep_header=False,export_file_type='csv'):

    path = path+export_file_type
    logging.info( f'Saving {dataset_type} features to {path} in format {export_file_type}')
    if 'idCampaign' in df:
        df.drop( ['idCampaign'], axis=1, inplace=True )

    logging.info( f'{dataset_type} data shape after preprocessing: {df.shape}' )
    if export_file_type =='zip':
        df.to_pickle(path=path)
    elif export_file_type=='csv':
        df.to_csv( path, header=keep_header, index=False )
    else:
        raise Exception('Wrong export file type')
    logging.info("Complete")



