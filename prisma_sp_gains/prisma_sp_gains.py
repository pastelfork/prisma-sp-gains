import json
from web3 import Web3

import reflex as rx

from rxconfig import config


class State(rx.State):
    """The app state."""
    eoa: str = ""
    input_validation_text: str = ""
    loading: bool = False

    collateral_data: list[list] = [
        ["wstETH", 0],
        ["rETH", 0],
        ["cbETH", 0],
        ["sfrxETH", 0],
        ["ETHx", 0],
        ["weETH", 0],
        ["ezETH", 0],
        ["rsETH", 0]
    ]

    def handle_query(self, eoa: str):
        if not Web3.is_address(eoa):
            self.input_validation_text = "Invalid address"
            return
        self.input_validation_text = ""
        self.eoa = eoa
        self.loading = True
        yield
        query_res = query_contracts(eoa)
        self.loading = False
        print(query_res)
        self.collateral_data[0][1] = query_res[0]
        self.collateral_data[1][1] = query_res[1]
        self.collateral_data[2][1] = query_res[2]
        self.collateral_data[3][1] = query_res[3]
        self.collateral_data[4][1] = query_res[4]
        self.collateral_data[5][1] = query_res[5]
        self.collateral_data[6][1] = query_res[6]
        self.collateral_data[7][1] = query_res[7]

        

def query_contracts(eoa):
    rpc_url: str = "https://eth.llamarpc.com"
    mkusd_sp_ca: str = "0xed8B26D99834540C5013701bB3715faFD39993Ba"
    ultra_sp_ca: str = "0x6953504F2f4537D7a7B4024508f321f7816BB6ED"
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    with open("./abi/sp_abi.json", "r",) as abi_file:
        abi = json.load(abi_file)

    mkusd_sp_contract = w3.eth.contract(
        address=mkusd_sp_ca,
        abi=abi
    ) # type: ignore
    ultra_sp_contract = w3.eth.contract(
        address=ultra_sp_ca,
        abi=abi
    ) # type: ignore

    wstETH_claimable = mkusd_sp_contract.functions.collateralGainsByDepositor(eoa, 0).call()
    wstETH_claimable = float(Web3.from_wei(wstETH_claimable, "ether"))
    rETH_claimable = mkusd_sp_contract.functions.collateralGainsByDepositor(eoa, 1).call()
    rETH_claimable = float(Web3.from_wei(rETH_claimable, "ether"))
    cbETH_claimable = mkusd_sp_contract.functions.collateralGainsByDepositor(eoa, 2).call()
    cbETH_claimable = float(Web3.from_wei(cbETH_claimable, "ether"))
    sfrxETH_claimable = mkusd_sp_contract.functions.collateralGainsByDepositor(eoa, 3).call()
    sfrxETH_claimable = float(Web3.from_wei(sfrxETH_claimable, "ether"))
    ETHx_claimable = mkusd_sp_contract.functions.collateralGainsByDepositor(eoa, 4).call()
    ETHx_claimable = float(Web3.from_wei(ETHx_claimable, "ether"))
    weETH_claimable = ultra_sp_contract.functions.collateralGainsByDepositor(eoa, 0).call()
    weETH_claimable = float(Web3.from_wei(weETH_claimable, "ether"))
    ezETH_claimable = ultra_sp_contract.functions.collateralGainsByDepositor(eoa, 1).call()
    ezETH_claimable = float(Web3.from_wei(ezETH_claimable, "ether"))
    rsETH_claimable = ultra_sp_contract.functions.collateralGainsByDepositor(eoa, 2).call()
    rsETH_claimable = float(Web3.from_wei(rsETH_claimable, "ether"))

    return wstETH_claimable, rETH_claimable, cbETH_claimable, sfrxETH_claimable, ETHx_claimable, weETH_claimable, ezETH_claimable, rsETH_claimable

def show_data(collateral_data: list):
    return rx.table.row(
        rx.table.cell(collateral_data[0]),
        rx.table.cell(collateral_data[1])
    )
def collateral_table():
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Collateral"),
                rx.table.column_header_cell("Claimable Amount"),
            )
        ),
        rx.table.body(
            rx.foreach(
                State.collateral_data,
                show_data
            )
        )
    )


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Prisma Stability Pool Collateral Claims Checker", size="7"),
            rx.text(
                "This is an unofficial, read-only checker for Stability Pool depositors. Enter your address below and the table will show your claimable collateral amounts. Created with 🌈 by ",
                rx.code(f"@pastelfork"),
                size="5",
            ),
            rx.debounce_input(
                rx.input(
                    placeholder="Your address here...",
                    value=State.eoa,
                    on_change=lambda e: State.handle_query(e),
                    width="100%"
                ),
                debounce_timeout=2000,
            ),
            rx.text(State.input_validation_text, color_scheme="red"),
            rx.cond(
                State.loading,
                rx.spinner(loading=True)
            ),
            collateral_table(),
            # rx.text(State.eoa),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )


app = rx.App()
app.add_page(index)
