from . import body
import os
import pandas as pd
from . import preprocess
from . import filter_db


def process_annotation(annotation, istable=None, sep='\t',
                        pathway_names=None, first_col_is_genes=False,
                        filter_redundant=False, pathway_similarity=0.2, min_pathway_length=20,
                        annotation_dir='annotation_dir', annotation_name=None):


    if not os.path.isdir(annotation_dir):
        os.mkdir(annotation_dir)

    if istable:
        annotation_table = annotation
        db_names, db_profiles, db_annotations, db_genes = \
            preprocess.get_profiles_from_table(annotation_table, sep=sep, first_col_is_genes=first_col_is_genes)

    else:
        db_names, db_profiles, db_annotations, db_genes = \
            preprocess.get_profiles(annotation, first_col_is_genes, pathway_names)

    if filter_redundant:
        db_names, db_annotations, db_profiles = filter_db.non_redundancy_sort_pre(db_names, db_annotations, db_profiles,
                                                                                  min_pathway_length,
                                                                                  pathway_similarity)
    if not annotation_name:
        annotation_name = annotation.split('/')[-1].split('.')[0]
    preprocess.dump_database(db_names, db_annotations, db_genes, db_profiles, annotation_name, annotation_dir)


def read_expression_file(expression_file, sep='\t', id_column=0, de_column=1):
    expression_column = de_column
    df = pd.read_csv(expression_file, sep=sep, skiprows=1, header=None)
    genes = df.iloc[:, id_column]
    expression_level = df.iloc[:, expression_column]
    return genes, expression_level


def run(de_genes, de_profile, annotation_name, annotation_dir='annotation_dir', output_name='stdout',
          de_ft=None, ann_ft=None, species='human', symmetric_expression=False,
          de_bins=10, a_bins=3, function='cmi', alpha=0.05, shuffles=1000, multipletest_method='None',
          max_heatmap_rows=20, export_heatmap=False, heatmap_bins=15,
          regulator=False, cmap_main='viridis', cmap_reg='viridis', filter_redundant=False, redundancy_ratio=0.1):

    db_bins = 2
    if output_name != 'stdout' and output_name != 'shut':
        if len(output_name.split('/')) != 1:
            output_dir = os.path.join(*output_name.split('/')[:-1])
        else:
            output_dir = output_name
            output_name += '/' + output_name

        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

    de_profile_discr, ann_names, ann_profiles, ann_annotations, abundance_profile, genes = body.process_input(
        de_profile, de_genes, annotation_name, de_ft, ann_ft, de_bins, a_bins,
        species, annotation_dir, symmetric_expression)

    cmis = body.count_cmi_for_profiles(de_profile_discr, ann_profiles, abundance_profile, de_bins,
                                       db_bins, a_bins, function)
    accepted_ann_profiles, z_scores = body.statistical_testing(cmis, de_profile_discr, ann_profiles,
                                                               abundance_profile, de_bins, db_bins, a_bins,
                                                               function, shuffles, alpha, multipletest_method,
                                                               filter_redundant, redundancy_ratio)
    if regulator:
        regulator_expression = body.get_rbp_expression(genes, ann_ft, de_profile,
                                                       accepted_ann_profiles, ann_names, ann_annotations, species,
                                                       annotation_dir)
    else:
        regulator_expression = None

    output = body.produce_output(accepted_ann_profiles, ann_profiles, ann_names, ann_annotations, cmis, z_scores,
                                 heatmap_bins, max_heatmap_rows, output_name, cmap_main, cmap_reg, regulator_expression,
                                 export_heatmap)
    if output_name == 'stdout' or output_name == 'shut':
        return output


