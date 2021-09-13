#
# Copyright (C) 2021 GrammaTech, Inc.
#
# This code is licensed under the MIT license. See the LICENSE file in
# the project root for license terms.
#
# This project is sponsored by the Office of Naval Research, One Liberty
# Center, 875 N. Randolph Street, Arlington, VA 22203 under contract #
# N68335-17-C-0700.  The content of the information does not necessarily
# reflect the position or policy of the Government and no official
# endorsement should be inferred.
#

"""
Utilities for constructing GTIRB IR in tests.
"""

import uuid
from typing import Dict, Iterable, Set, Tuple, Type, TypeVar, Union

import gtirb


def create_test_module(
    file_format: gtirb.Module.FileFormat,
    isa: gtirb.Module.ISA,
    binary_type: Iterable[str] = None,
) -> Tuple[gtirb.IR, gtirb.Module]:
    """
    Creates a test GTIRB module and returns the IR object and module object.
    """
    ir = gtirb.IR()
    m = gtirb.Module(isa=isa, file_format=file_format, name="test")
    m.ir = ir

    add_standard_aux_data_tables(m)
    if binary_type:
        m.aux_data["binaryType"].data = list(binary_type)

    return ir, m


def add_standard_aux_data_tables(m: gtirb.Module) -> None:
    """
    Adds aux data tables that ddisasm normally produces. This helps avoid
    every test needing to know the schemas.
    """
    m.aux_data["binaryType"] = gtirb.AuxData(
        type_name="sequence<string>", data=list()
    )
    m.aux_data["cfiDirectives"] = gtirb.AuxData(
        type_name=(
            "mapping<Offset,sequence<tuple<string,sequence<int64_t>,UUID>>>"
        ),
        data=dict(),
    )
    m.aux_data["comments"] = gtirb.AuxData(
        type_name="mapping<Offset,string>", data=dict()
    )
    m.aux_data["elfSectionProperties"] = gtirb.AuxData(
        type_name="mapping<UUID,tuple<uint64_t,uint64_t>>", data=dict()
    )
    m.aux_data["encodings"] = gtirb.AuxData(
        type_name="mapping<UUID,string>", data=dict()
    )
    m.aux_data["functionBlocks"] = gtirb.AuxData(
        type_name="mapping<UUID,set<UUID>>", data=dict()
    )
    m.aux_data["functionEntries"] = gtirb.AuxData(
        type_name="mapping<UUID,set<UUID>>", data=dict()
    )
    m.aux_data["functionNames"] = gtirb.AuxData(
        type_name="mapping<UUID,UUID>", data=dict()
    )
    m.aux_data["libraries"] = gtirb.AuxData(
        type_name="sequence<string>", data=list()
    )
    m.aux_data["libraryPaths"] = gtirb.AuxData(
        type_name="sequence<string>", data=list()
    )
    m.aux_data["padding"] = gtirb.AuxData(
        type_name="mapping<Offset,uint64_t>", data=dict()
    )
    m.aux_data["symbolForwarding"] = gtirb.AuxData(
        type_name="mapping<UUID,UUID>", data=dict()
    )
    m.aux_data["symbolicExpressionSizes"] = gtirb.AuxData(
        type_name="mapping<Offset,uint64_t>", data=dict()
    )
    m.aux_data["SCCs"] = gtirb.AuxData(
        type_name="mapping<UUID,int64_t>", data=dict()
    )

    if m.file_format == gtirb.Module.FileFormat.ELF:
        m.aux_data["alignment"] = gtirb.AuxData(
            type_name="mapping<UUID,uint64_t>", data=dict()
        )
        m.aux_data["dynamicEntries"] = gtirb.AuxData(
            type_name="set<tuple<string,uint64_t>>", data=set()
        )
        m.aux_data["elfSymbolInfo"] = gtirb.AuxData(
            type_name=(
                "mapping<UUID,tuple<uint64_t,string,string,string,uint64_t>>"
            ),
            data=dict(),
        )
        m.aux_data["elfSymbolTabIdxInfo"] = gtirb.AuxData(
            type_name="mapping<UUID,sequence<tuple<string,uint64_t>>>",
            data=dict(),
        )

    elif m.file_format == gtirb.Module.FileFormat.PE:
        m.aux_data["peExportEntries"] = gtirb.AuxData(
            type_name="sequence<tuple<uint64_t,int64_t,string>>", data=list()
        )
        m.aux_data["peExportedSymbols"] = gtirb.AuxData(
            type_name="sequence<UUID>", data=list()
        )
        m.aux_data["peImportEntries"] = gtirb.AuxData(
            type_name="sequence<tuple<uint64_t,int64_t,string,string>>",
            data=list(),
        )
        m.aux_data["peImportedSymbols"] = gtirb.AuxData(
            type_name="sequence<UUID>", data=list()
        )
        m.aux_data["peResources"] = gtirb.AuxData(
            type_name="sequence<tuple<sequence<uint8_t>,Offset,uint64_t>>",
            data=list(),
        )


def add_section(
    m: gtirb.Module,
    name: str,
    address: int = None,
    flags: Set[gtirb.Section.Flag] = {
        gtirb.Section.Flag.Readable,
        gtirb.Section.Flag.Loaded,
        gtirb.Section.Flag.Initialized,
    },
) -> Tuple[gtirb.Section, gtirb.ByteInterval]:
    """
    Adds a section to the module and creates a byte interval for it.
    """
    s = gtirb.Section(name=name, flags=flags)
    s.module = m
    bi = gtirb.ByteInterval(contents=b"", address=address)
    bi.section = s
    return s, bi


def add_text_section(
    m: gtirb.Module, address: int = None
) -> Tuple[gtirb.Section, gtirb.ByteInterval]:
    """
    Creates the appropriate text section for a module.
    """
    assert m.file_format in (
        gtirb.Module.FileFormat.ELF,
        gtirb.Module.FileFormat.PE,
    )
    return add_section(
        m,
        ".text",
        address,
        flags={
            gtirb.Section.Flag.Readable,
            gtirb.Section.Flag.Executable,
            gtirb.Section.Flag.Loaded,
            gtirb.Section.Flag.Initialized,
        },
    )


def add_data_section(
    m: gtirb.Module, address: int = None
) -> Tuple[gtirb.Section, gtirb.ByteInterval]:
    """
    Creates the appropriate data section for a module.
    """
    assert m.file_format in (
        gtirb.Module.FileFormat.ELF,
        gtirb.Module.FileFormat.PE,
    )
    return add_section(
        m,
        ".data",
        address,
        flags={
            gtirb.Section.Flag.Readable,
            gtirb.Section.Flag.Writable,
            gtirb.Section.Flag.Loaded,
            gtirb.Section.Flag.Initialized,
        },
    )


BlockT = TypeVar("BlockT", bound=gtirb.ByteBlock)


def add_byte_block(
    byte_interval: gtirb.ByteInterval,
    block_type: Type[BlockT],
    content: bytes,
    symbolic_expressions: Dict[int, gtirb.SymbolicExpression] = None,
) -> BlockT:
    """
    Adds a block to a byte interval, setting up its contents and optionally
    its symbolic expressions.
    """
    b = block_type(offset=byte_interval.size, size=len(content))
    b.byte_interval = byte_interval
    byte_interval.contents += content
    if symbolic_expressions:
        for off, expr in symbolic_expressions.items():
            assert isinstance(expr, gtirb.SymbolicExpression)
            byte_interval.symbolic_expressions[byte_interval.size + off] = expr
    byte_interval.size += len(content)
    return b


def add_code_block(
    byte_interval: gtirb.ByteInterval,
    content: bytes,
    symbolic_expressions: Dict[int, gtirb.SymbolicExpression] = None,
) -> gtirb.CodeBlock:
    """
    Adds a code block to a byte interval, setting up its contents and
    optionally its symbolic expressions.
    """
    return add_byte_block(
        byte_interval, gtirb.CodeBlock, content, symbolic_expressions
    )


def add_data_block(
    byte_interval: gtirb.ByteInterval,
    content: bytes,
    symbolic_expressions: Dict[int, gtirb.SymbolicExpression] = None,
) -> gtirb.DataBlock:
    """
    Adds a data block to a byte interval, setting up its contents and
    optionally its symbolic expressions.
    """
    return add_byte_block(
        byte_interval, gtirb.DataBlock, content, symbolic_expressions
    )


def add_proxy_block(m: gtirb.Module) -> gtirb.ProxyBlock:
    """
    Creates a proxy block and adds it to the module.
    """
    b = gtirb.ProxyBlock()
    m.proxies.add(b)
    return b


def add_symbol(
    module: gtirb.Module, name: str, payload: gtirb.Block = None
) -> gtirb.Symbol:
    """
    Creates a symbol and adds it to the module.
    """
    sym = gtirb.Symbol(name, payload=payload)
    sym.module = module
    return sym


def add_elf_symbol_info(
    module: gtirb.Module,
    sym: gtirb.Symbol,
    size: int,
    type: str,
    binding: str = "GLOBAL",
    visibility: str = "DEFAULT",
    section_index: int = 0,
) -> None:
    """
    Adds an entry to the elfSymbolInfo aux data table.
    """
    module.aux_data["elfSymbolInfo"].data[sym] = (
        size,
        type,
        binding,
        visibility,
        section_index,
    )


def add_function(
    module: gtirb.Module,
    sym_or_name: Union[str, gtirb.Symbol],
    entry_block: gtirb.CodeBlock,
    other_blocks: Set[gtirb.CodeBlock] = set(),
) -> uuid.UUID:
    """
    Adds a function to all the appropriate aux data.
    """
    if isinstance(sym_or_name, str):
        func_sym = add_symbol(module, sym_or_name, entry_block)
    elif isinstance(sym_or_name, gtirb.Symbol):
        func_sym = sym_or_name
    else:
        assert False, "Invalid symbol name"

    entry_blocks = {entry_block}
    all_blocks = entry_blocks | other_blocks

    func_uuid = uuid.uuid4()
    module.aux_data["functionNames"].data[func_uuid] = func_sym
    module.aux_data["functionEntries"].data[func_uuid] = entry_blocks
    module.aux_data["functionBlocks"].data[func_uuid] = all_blocks

    if (
        module.file_format == gtirb.Module.FileFormat.ELF
        and "elfSymbolInfo" in module.aux_data
    ):
        add_elf_symbol_info(module, func_sym, 0, "FUNC")

    return func_uuid


def add_edge(
    cfg: gtirb.CFG,
    source: gtirb.CfgNode,
    target: gtirb.CfgNode,
    edge_type: gtirb.Edge.Type,
    *,
    conditional: bool = False,
    direct: bool = True,
) -> gtirb.Edge:
    """
    Creates and adds an edge to a CFG.
    """
    edge = gtirb.Edge(
        source=source,
        target=target,
        label=gtirb.Edge.Label(
            type=edge_type, conditional=conditional, direct=direct
        ),
    )
    cfg.add(edge)
    return edge


def set_all_blocks_alignment(module: gtirb.Module, alignment: int) -> None:
    """
    Sets the alignment of all blocks in a module to a specific value.
    """
    for block in module.byte_blocks:
        module.aux_data["alignment"].data[block] = alignment
