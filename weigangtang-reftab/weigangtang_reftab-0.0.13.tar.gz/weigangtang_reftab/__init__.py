import numpy as np
import pandas as pd

import os
import re
import glob
import string

from tabulate import tabulate

header_full = ['Link', 'Title', 'Abbr', 'Year', 'Journal', 'Authors', 'Vol',
               'Pages', 'Keyword']
header_must = ['Title', 'Year', 'Journal', 'Authors', 'Vol', 'Pages']


class pcolors:
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    FAIL = '\033[1;91m'
    WARNING = '\033[1;93m'


# ----------------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------------
def check_pattern(target_string, pattern):
    return bool(re.search(pattern, target_string))


def is_year_format_correct(year):
    return check_pattern(year, '^[0-9]{4}[a-z]?$')


def is_author_format_correct(authors_string):
    author_list = authors_string.split('; ')
    for author in author_list:
        if author != '…':
            if not check_pattern(author, '^[a-zA-Z- ]{2,20},( [A-Z].){1,5}$'):
                return False
    return True


def auto_correct_author_string(author_string):
    author_list = []
    for author in author_string.split(';'):
        # remove space at start
        while author[0] == ' ':
            author = author[1:]
        # remove space at end
        while author[-1] == ' ':
            author = author[:-1]
        # add '.' after name short
        pattern = r'([A-Z](?![\.|A-Z|a-z]))', r'\1.'  # must place 'r' ahead
        author = re.sub(pattern, author)
        author_list.append(author)
    return '; '.join(author_list)


def auto_correct_author_column(df):
    author_string_list = []
    for author_string in df['Authors'].values:
        author_string = auto_correct_author_string(author_string)
        author_string_list.append(author_string)
    return author_string_list


def auto_fill_abbr(df):
    abbr_list = []
    for authors, year in df[['Authors', 'Year']].values:
        if is_year_format_correct(year) & is_author_format_correct(authors):
            author_name_list = [
                item.split(', ')[0] for item in authors.split('; ')
            ]  # last name
            n_author = len(author_name_list)
            if n_author == 1:
                author = author_name_list[0]
            if n_author == 2:
                author = ' & '.join(author_name_list)
            if n_author >= 3:
                author = author_name_list[0] + ' et al.'
            abbr_list.append(', '.join([author, str(year)]))
        else:
            abbr_list.append('')
    return abbr_list


def auto_fill_link(df):
    link_list = []
    for abbr, journal in df[['Abbr', 'Journal']].values:
        name, year = abbr.split(', ')
        name = name.replace('et al.', 'et al')
        journal = journal + '.pdf'
        link = '_'.join([name, year, journal])
        link_list.append(link)
    return link_list


def read_ref_workbook(workbook_fpath):
    workbook_dict = {}
    workbook = pd.ExcelFile(workbook_fpath)
    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(workbook, sheet_name, index_col=0).astype(str)
        df = df.replace('nan', '')
        workbook_dict.update({sheet_name: df})
    return workbook_dict


# DataFrame must have the identical header
def merge_ref_workbook(workbook_dict):
    df_list = []
    for sheet_name, df in workbook_dict.items():
        if 'Keyword' not in df.columns:
            if sheet_name == 'No Category':
                keyword = ''
            elif sheet_name == 'Important':
                keyword = '*'
            else:
                keyword = sheet_name
            df['Keyword'] = keyword
        df_list.append(df)
    df = pd.concat(df_list, axis=0).sort_index()
    df = merge_duplicated_ref(df)
    return df


def check_ref_workbook(workbook_dict):

    # find sheet with missing columns
    for sheet_name, df_ref in workbook_dict.items():
        header = df_ref.columns.tolist()
        miscol = list(set(header_must).difference(header))
        if miscol:
            print('<{}> misses columns of {}'.format(sheet_name, miscol))
            return False

    # find reference with incorrect format in authors and year
    for sheet_name, df_ref in workbook_dict.items():
        sel_ref_1, sel_ref_2 = [], []
        for link, row in df_ref.iterrows():
            if not is_author_format_correct(row['Authors']):
                sel_ref_1.append(link)
            if not is_year_format_correct(row['Year']):
                sel_ref_2.append(link)
        if sel_ref_1:
            sel_author_list = df_ref.loc[sel_ref_1, ['Authors']]
            print('<{}> has incorrect format of Authors.'.format(sheet_name))
            print(tabulate(sel_author_list, tablefmt='psql'))
        if sel_ref_2:
            sel_year_list = df_ref.loc[sel_ref_2, ['Year']]
            print('<{}> has incorrect format of Year.'.format(sheet_name))
            print(tabulate(sel_year_list, tablefmt='psql'))

        # if find incorrect author or year, it won't examine following sheets
        if sel_ref_1 or sel_ref_2:
            return False

    return True


def clean_ref_table(df_ref):
    df = df_ref.copy()
    df['Authors'] = auto_correct_author_column(df)
    df['Abbr'] = auto_fill_abbr(df)
    df.index = auto_fill_link(df)
    df.index.name = 'Link'
    df = sort_header(df)
    df = df.sort_index()
    return df


def clean_ref_workbook(workbook_dict):
    wb = workbook_dict.copy()
    for sheet_name, df_ref in wb.items():
        wb[sheet_name] = clean_ref_table(df_ref)
    return wb


# merge duplicated references
def merge_duplicated_ref(df_ref):

    def merge_keyword(x):
        return ', '.join([i for i in x if i != ''])

    def clean_keyword(x):
        return ', '.join(np.unique(x.split(', ')))

    df = df_ref.groupby('Link').first()
    df['Keyword'] = df_ref.groupby('Link')['Keyword'].apply(merge_keyword)
    df['Keyword'] = df['Keyword'].apply(clean_keyword)  # sort by alphabet
    return df


def get_pdf_list(readcube_fpath, show_invalid=True):
    fpath_list = glob.glob(readcube_fpath + '/*.pdf')
    fname_list = sorted([os.path.split(fpath)[1] for fpath in fpath_list])

    sel_fname_list = []
    for fname in fname_list:
        if len(fname.split('_')) == 3:
            sel_fname_list.append(fname)

    if show_invalid:
        unsel_fname_list = sorted(set(fname_list).difference(sel_fname_list))
        if len(unsel_fname_list) > 0:
            text = 'PDF with Non-Standard Name:'
            print(pcolors.BOLD + text + pcolors.END)  # print bold
            for fname in unsel_fname_list:
                if 'supplement' not in fname:
                    fname = pcolors.RED + fname + pcolors.END
                print(fname)

    return sel_fname_list


def create_df_from_pdf_name(pdf_name_list):
    df = pd.DataFrame(columns=header_full)
    for i, link in enumerate(pdf_name_list):
        name, year, journal = link.split('_')
        name = name.replace('et al', 'et al.')
        abbr = ', '.join([name, year])
        journal = journal[:-4]  # remove .pdf from file name
        df.loc[i, ['Abbr', 'Year', 'Journal', 'Link']] = [
            abbr, year, journal, link]
    df = df.set_index('Link').sort_index()
    return df


def sort_header(df):
    # item not in header are ignored
    sorted_header = [item for item in header_full if item in df.columns]
    return df[sorted_header]


# workbook: Dictionary of DataFrame, e.g. {'Sheet1': df_ref}
# determine the standard format of reference table (in excle)
def save_workbook_to_excel(
        out_fpath, workbook, hyperlink_base, overwrite=False):

    column_width_dict = {
        'Link': 60, 'Title': 80, 'Abbr': 24, 'Year': 8, 'Journal': 35,
        'Authors': 30, 'Vol': 6, 'Pages': 12, 'Keyword': 20,
    }

    fmt_dict = {
        'text': {
            'font_name': 'Times New Roman', 'font_size': 12
        },
        'header': {
            'font_name': 'Times New Roman', 'font_size': 12, 'bold': True,
        },
        'url': {
            'font_name': 'Times New Roman', 'font_size': 12, 'color': 'blue',
        },
    }

    exists = os.path.exists(out_fpath)

    if not exists or overwrite:

        writer = pd.ExcelWriter(out_fpath, engine='xlsxwriter')

        hyperlink_base = os.path.abspath(hyperlink_base)
        hyperlink_base += '/'  # must add '/' at end, or hyperlink is invalid
        writer.book.set_properties({'hyperlink_base': hyperlink_base})

        for sheet_name, df in workbook.items():

            df = sort_header(df)

            df.to_excel(writer, sheet_name=sheet_name)
            nrow, ncol = df.shape

            worksheet = writer.sheets[sheet_name]

            # set header format
            header = df.reset_index().columns.tolist()
            header_fmt = writer.book.add_format(fmt_dict['header'])
            worksheet.write_row(0, 0, header, header_fmt)

            # set content format and column width (add one for index column)
            column_width_list = [column_width_dict[item] for item in header]
            for i in range(ncol + 1):
                text_fmt = writer.book.add_format(fmt_dict['text'])
                worksheet.set_column(i, i, column_width_list[i], text_fmt)

            # set url format (overwrite first column)
            for i in range(nrow):
                url_fmt = writer.book.add_format(fmt_dict['url'])
                worksheet.write_url(i + 1, 0, df.index[i], url_fmt)

        writer.save()

    else:
        print('Not Allow Overwrite!')


def save_df_to_excel(
        out_fpath, df_ref, hyperlink_base, overwrite=False):

    workbook = {'': df_ref}  # replace '' with 'Sheet1'
    save_workbook_to_excel(out_fpath, workbook, hyperlink_base, overwrite)


def save_df_to_latex(out_fpath, df_ref, overwrite=False):

    exists = os.path.exists(out_fpath)

    if not exists or overwrite:

        df_ref = df_ref.copy()

        df_ref['Label'] = ''
        for indx, item in df_ref.iterrows():
            label = item['Abbr']
            label = label.replace(' & ', ' ')
            label = label.replace(',', '')
            label = label.replace('.', '')
            label = label.replace(' ', '-')
            df_ref.loc[indx, 'Label'] = label

        # add a letter for duplicated abbr
        a2z = string.ascii_lowercase
        for target_label in np.unique(df_ref['Label']):
            indx = df_ref['Label'] == target_label
            n_dup = sum(indx)
            if n_dup > 1:
                df_ref.loc[indx, 'Label'] = [
                    target_label + char for char in a2z[:n_dup]]
        df_ref = df_ref.sort_values('Label')

        refs = []
        for indx, item in df_ref.iterrows():
            lines = []
            lines.append('@article{' + item['Label'] + ', ')
            lines.append(
                '\t author = \"{}\", '.format(
                    item['Authors'].replace(
                        ';', ' and')))
            lines.append('\t title = \"{}\", '.format(item['Title']))
            lines.append('\t year = \"{}\", '.format(item['Year']))
            lines.append('\t journal = \"{}\", '.format(item['Journal']))
            if item['Vol'] != '-':
                lines.append('\t volume = \"{}\", '.format(item['Vol']))
            if item['Pages'] != '-':
                lines.append('\t pages = \"{}\", '.format(item['Pages']))
            lines.append('}')

            refs.append('\n'.join(lines))

        if exists:
            os.remove(out_fpath)

        with open(out_fpath, 'a') as f:
            f.write('\n\n'.join(refs))

    else:
        print('Not Allow Overwrite!')

# ----------------------------------------------------------------------------------
# Class
# ----------------------------------------------------------------------------------


class RefTab():

    # reftab: DataFrame
    def __init__(self, reftab, hyperlink_base):

        assert set(header_must).issubset(reftab.columns)

        self.df = reftab.copy()

        # autofill abbr
        self.df['Abbr'] = auto_fill_abbr(self.df)

        # autofill link
        self.df.index = auto_fill_link(self.df)
        self.df.index.name = 'Link'

        # autofill keywords
        if 'Keyword' not in self.df.columns:
            self.df['Keyword'] = ''
        self.df['Keyword'] = self.df['Keyword'].replace('Sheet1', '')

        hyperlink_base = os.path.abspath(hyperlink_base)
        self.hyperlink_base = hyperlink_base + '/'

        self.pdf_list = get_pdf_list(self.hyperlink_base, show_invalid=False)

    def update(self, new_reftab):
        self.df = new_reftab

    def find_incomplete_ref(self):
        return self.df[self.df.isna().any(axis=1)]

    def find_duplicated_ref(self):
        return self.df[self.df.index.duplicated(keep=False)]

    def find_duplicated_ref_by_abbr(self):
        return self.df[self.df.duplicated('Abbr', keep=False)]

    def find_nolink_ref(self):
        nolink_fname_list = sorted(
            set(self.df.index).difference(self.pdf_list))
        return self.df.loc[nolink_fname_list, :]

    def find_unlisted_pdf(self):
        unlisted_pdf_list = sorted(
            set(self.pdf_list).difference(self.df.index))
        return unlisted_pdf_list

    def find_invalid_pdf_name(self):
        invalid_name_pdf_list = [
            name for name in self.pdf_list if len(name.split('-')) != 3]
        return invalid_name_pdf_list

    def get_unique_keywords(self):
        keyword_list = []
        for keyword in self.df['Keyword']:
            keyword_list += keyword.split(', ')
        return np.unique(keyword_list).tolist()

    def get_unique_ref(self):
        return merge_duplicated_ref(self.df)

    def subset_ref_by_keyword(self, keyword):
        sel_idx = []
        for keyword_string in self.df['Keyword']:
            keyword_list = keyword_string.split(', ')
            sel_idx.append(keyword in keyword_list)
        return self.df.iloc[sel_idx, :]

    def subset_ref_by_abbr(self, sel_abbr):
        df = self.get_unique_ref()
        df = self.df.drop(columns='Keyword')

        all_abbr = set(df['Abbr'].values)
        sel_abbr = set(np.unique(sel_abbr))

        diff = sorted(sel_abbr.difference(all_abbr))
        if len(diff) > 0:
            print('Not Found Related References:')
            print('\n'.join(diff))

        union = sorted(sel_abbr.intersection(all_abbr))
        return df[df['Abbr'].isin(union)]

    def save_to_excel(
            self, out_fpath, overwrite=False, split_by_keyword=False):
        if split_by_keyword:
            wb = {}
            for keyword in self.get_unique_keywords():
                df_sel = self.subset_ref_by_keyword(keyword)
                if keyword == '':
                    sheet_name = 'No Category'
                elif keyword == '*':
                    sheet_name = 'Important'
                else:
                    sheet_name = keyword
                wb.update({sheet_name: df_sel})
            save_workbook_to_excel(
                out_fpath, wb, self.hyperlink_base, overwrite)
        else:
            save_df_to_excel(
                out_fpath, self.df, self.hyperlink_base, overwrite)

    def save_to_latex(self, out_fpath, overwrite=False):
        save_df_to_latex(out_fpath, self.df, overwrite)
