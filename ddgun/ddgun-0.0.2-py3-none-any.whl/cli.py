# aaindexN vengono da https://www.genome.jp/ftp/db/community/aaindex/
from ddgun import funcs_seq
#import funcs_3d
from ddgun.aa import Substitution
from ddgun import ddgun
from ddgun.profile import Profile
import click
import sys

class SubstitutionParam(click.ParamType):
    '''Click parameter class for substitutions'''
    name = 'amino acid substitution'
    def convert(self, value, param, ctx):
        if isinstance(value, Substitution):
            return value
        try:
            return Substitution.parse(value)
        except Exception as e:
            self.fail(f"{value!r} is not a valid {self.name}", param, ctx)

class ProfileParam(click.ParamType): # TODO check handling of file not found
#and other exception
    '''Click parameter class for profiles'''
    name = 'protein profile'
    def convert(self, value, param, ctx):
        if isinstance(value, Profile):
            return value
        try:
            return Profile(value)
        except Exception as e:
            self.fail(f"{value!r} is not a valid {self.name}", param, ctx)

@click.group()
def cli():
    pass


#def smart_open(path, mode):
#    import gzip
#    return (gzip.open if path.endswith('.gz') else open)(path, mode)

@cli.command()
@click.argument('sub', type=SubstitutionParam())
@click.argument('profile', type=click.Path(exists=True, readable=True))
def seq(profile, sub):
    '''Predict DDG of SUB using PROFILE'''
    #click.echo(f"{aa_from}{aa_pos + 1}{aa_to}")
    if False: #debug
        import pandas
        m = ddgun.parse_aa_change(sub)
        p = pandas.read_csv(profile, sep='\s+', index_col=0)
        ddg = ddgun.ddgun_seq_old(p, m)
        click.echo(ddg)

    p = Profile(profile)
    ddg = ddgun.ddgun_seq(s, p)
    click.echo(ddg)

@cli.command()
@click.argument('sub', type=SubstitutionParam())
@click.argument('profile', type=click.Path(exists=True, readable=True))
@click.argument('structure', type=click.Path(exists=True, readable=True))
@click.argument('chain')
@click.argument('access', type=click.Path(exists=True, readable=True))
def struct(sub, profile, structure, chain, access):
    '''Predict DDG of SUB using PROFILE'''
    ddg = ddgun.ddgun_3d(sub, profile, structure, chain, access)
    click.echo(ddg)

# TEST: ddgun p3d I33A data/2ocjA.prof data/2ocj.pdb A data/2ocjA.dssp_parsed


@cli.command()
@click.option('--output', type=click.Path(writable=True), help='output file, defaults to stdout')
@click.argument('msa', type=click.Path(exists=True, readable=True))
def mkprof(msa, output):
    '''Convert MSA into a profile table.

MSA multiple sequence alignments in psiblast format'''
    p = Profile.from_msa(msa)
    if output is None:
        output = sys.stdout
    p.write(output)
