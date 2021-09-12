import os
from scipy import stats


################################################# subsample OTU table ##################################################

# otu_table           = '/Users/songweizhi/Desktop/otu_table2.txt'
# sample_id           = ['57884', '57885', '57886']
# otu_table_subset    = '/Users/songweizhi/Desktop/otu_table_57884_57885_57886.txt'
# otu_table_combined  = '/Users/songweizhi/Desktop/otu_table_BH_ER_050417.txt'
#
# otu_table_subset_handle = open(otu_table_subset, 'w')
# otu_table_combined_handle = open(otu_table_combined, 'w')
# otu_table_subset_handle.write('ID\t%s\n' % '\t'.join(sample_id))
# otu_table_combined_handle.write('ID\tBH_ER_050417\n')
# sample_index_dict = {}
# for each_line in open(otu_table):
#     each_line_split = each_line.strip().split('\t')
#     if each_line.startswith('34830'):
#         for each_sample in sample_id:
#             sample_index = each_line_split.index(each_sample) + 1
#             sample_index_dict[each_sample] = sample_index
#     else:
#         extract_element_list = []
#         for each_sample in sample_id:
#             sample_index = sample_index_dict.get(each_sample)
#             sample_value = each_line_split[sample_index]
#             extract_element_list.append(int(sample_value))
#         if extract_element_list != [0, 0, 0]:
#             otu_table_subset_handle.write('%s\t%s\n' % (each_line_split[0], '\t'.join([str(i) for i in extract_element_list])))
#             otu_table_combined_handle.write('%s\t%s\n' % (each_line_split[0], sum(extract_element_list)))
# otu_table_subset_handle.close()
# otu_table_combined_handle.close()


############################################ get metagenome functional table ###########################################

# diamond_op          = '/Users/songweizhi/Desktop/BH_ER_050417_vs_Tax4Fun2_KEGG_best_hit.tab'
# metagenome_fun_tab  = '/Users/songweizhi/Desktop/BH_ER_050417_metagenome_fun.txt'
#
# identified_ko_set= set()
# ko_count_dict = {}
# total_count = 0
# for each_line in open(diamond_op):
#     each_line_split = each_line.strip().split('\t')
#     subject = each_line_split[1]
#     subject_list = [subject]
#     if len(subject) > 6:
#         subject_list = subject.split(':')
#     for each_ko in subject_list:
#         identified_ko_set.add(each_ko)
#         total_count += 1
#         if each_ko not in ko_count_dict:
#             ko_count_dict[each_ko] = 1
#         else:
#             ko_count_dict[each_ko] += 1
#
# metagenome_fun_tab_handle = open(metagenome_fun_tab, 'w')
# metagenome_fun_tab_handle.write('KO\tMetagenome\n')
# for each_ko in sorted([i for i in identified_ko_set]):
#     ko_pct = ko_count_dict[each_ko]/total_count
#     metagenome_fun_tab_handle.write('%s\t%s\n' % (each_ko, ko_pct))
# metagenome_fun_tab_handle.close()


########################################################################################################################

fun_table_metagenome               = '/Users/songweizhi/Desktop/Tax4Fun2_wd/BH_ER_050417_metagenome_fun.txt'
fun_table_Tax4Fun2_default         = '/Users/songweizhi/Desktop/Tax4Fun2_wd/Kelp_57884_57885_57886_default_Ref99NR/functional_prediction.txt'
fun_table_Tax4Fun2_no_linked_MAG   = '/Users/songweizhi/Desktop/Tax4Fun2_wd/Kelp_57884_57885_57886_no_linked_MAGs_Ref99NR/functional_prediction.txt'
fun_table_Tax4Fun2_with_linked_MAG = '/Users/songweizhi/Desktop/Tax4Fun2_wd/Kelp_57884_57885_57886_with_linked_16S_Ref99NR/functional_prediction.txt'


all_identified_ko_set = set()
metagenome_fun_dict = {}
for each_line in open(fun_table_metagenome):
    if not each_line.startswith('KO'):
        each_line_split = each_line.strip().split('\t')
        ko_id = each_line_split[0]
        ko_abun = float(each_line_split[1])
        metagenome_fun_dict[ko_id] = ko_abun
        all_identified_ko_set.add(ko_id)

Tax4Fun2_default_fun_dict = {}
for each_line in open(fun_table_Tax4Fun2_default):
    if not each_line.startswith('KO'):
        each_line_split = each_line.strip().split('\t')
        ko_id = each_line_split[0]
        ko_abun = float(each_line_split[1])
        Tax4Fun2_default_fun_dict[ko_id] = ko_abun
        all_identified_ko_set.add(ko_id)

Tax4Fun2_no_linked_MAG_fun_dict = {}
for each_line in open(fun_table_Tax4Fun2_no_linked_MAG):
    if not each_line.startswith('KO'):
        each_line_split = each_line.strip().split('\t')
        ko_id = each_line_split[0]
        ko_abun = float(each_line_split[1])
        Tax4Fun2_no_linked_MAG_fun_dict[ko_id] = ko_abun
        all_identified_ko_set.add(ko_id)

Tax4Fun2_with_linked_MAG_fun_dict = {}
if os.path.isfile(fun_table_Tax4Fun2_with_linked_MAG) is True:
    for each_line in open(fun_table_Tax4Fun2_with_linked_MAG):
        if not each_line.startswith('KO'):
            each_line_split = each_line.strip().split('\t')
            ko_id = each_line_split[0]
            ko_abun = float(each_line_split[1])
            Tax4Fun2_with_linked_MAG_fun_dict[ko_id] = ko_abun
            all_identified_ko_set.add(ko_id)

fun_abun_list_metagenome = []
fun_abun_list_Tax4Fun2_default = []
fun_abun_list_Tax4Fun2_no_linked_MAG = []
fun_abun_list_Tax4Fun2_with_linked_MAG = []
for each_ko in sorted([i for i in all_identified_ko_set]):
    fun_abun_list_metagenome.append(metagenome_fun_dict.get(each_ko, 0))
    fun_abun_list_Tax4Fun2_default.append(Tax4Fun2_default_fun_dict.get(each_ko, 0))
    fun_abun_list_Tax4Fun2_no_linked_MAG.append(Tax4Fun2_no_linked_MAG_fun_dict.get(each_ko, 0))
    fun_abun_list_Tax4Fun2_with_linked_MAG.append(Tax4Fun2_with_linked_MAG_fun_dict.get(each_ko, 0))

default_rho, default_pval                 = stats.spearmanr(fun_abun_list_metagenome, fun_abun_list_Tax4Fun2_default)
no_linked_MAG_rho, no_linked_MAG_pval     = stats.spearmanr(fun_abun_list_metagenome, fun_abun_list_Tax4Fun2_no_linked_MAG)
with_linked_MAG_rho, with_linked_MAG_pval = stats.spearmanr(fun_abun_list_metagenome, fun_abun_list_Tax4Fun2_with_linked_MAG)

print('metagenome_vs_Tax4Fun2_default_spearman\t%s\t%s'         % (float("{0:.4f}".format(default_rho)), float("{0:.4f}".format(default_pval))))
print('metagenome_vs_Tax4Fun2_no_linked_MAG_spearman\t%s\t%s'   % (float("{0:.4f}".format(no_linked_MAG_rho)), float("{0:.4f}".format(no_linked_MAG_pval))))
print('metagenome_vs_Tax4Fun2_with_linked_MAG_spearman\t%s\t%s' % (float("{0:.4f}".format(with_linked_MAG_rho)), float("{0:.4f}".format(with_linked_MAG_pval))))

'''
metagenome_vs_Tax4Fun2_default_spearman	        0.599	0.0
metagenome_vs_Tax4Fun2_no_linked_MAG_spearman	0.7837	0.0
metagenome_vs_Tax4Fun2_with_linked_MAG_spearman	0.8192	0.0
'''