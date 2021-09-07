import sqlalchemy as sa

FSHARADAR_DB_VERSION = 1

db_table_names = frozenset({
    'tickers',
    'version_info',
})

metadata = sa.MetaData()

tickers_tbl = sa.Table(
    'tickers',
    metadata,
    # Permanent Ticker Symbol
    sa.Column(
        'sid',   
        sa.Integer,
        unique=True,
        nullable=False,
        primary_key=True,
    ),
    # Ticker Symbol
    sa.Column('ticker', sa.Text),
    # Issuer Name
    sa.Column('name', sa.Text), 
    # Stock Exchange
    sa.Column('exchange', sa.Text),  
    # Is Delisted?
    sa.Column('isdelisted', sa.Text),   # Bool 
    # Issuer Category
    sa.Column('category', sa.Text), 
)

version_info_tbl = sa.Table(
    'version_info',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        unique=True,
        nullable=False,
        primary_key=True,
    ),
    sa.Column(
        'version',
        sa.Integer,
        unique=True,
        nullable=False,
    ),
    # This constraint ensures a single entry in this table
    sa.CheckConstraint('id <= 1'),
)

