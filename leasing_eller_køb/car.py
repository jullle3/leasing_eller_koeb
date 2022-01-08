import pprint
from datetime import date
import matplotlib.pyplot as plt


def pexit(s):
    pprint.pprint(s)
    print(type(s))
    if hasattr(s, "__len__"):
        print(len(s))
    exit()


class Car:
    """
    TODO: Beregn om det kan betale sig først at lease, for så at købe bilen når prisen er faldet tilstrækkeligt
    Se afgifts satser:
    https://skat.dk/SKAT.aspx?oid=2234529
    """

    registration_fees = [
        {"rate": 0.25, "amount": 65000},
        {"rate": 0.85, "amount": 137200},
        {"rate": 1.50, "amount": 999999999},  # Resten af bilens værdi
    ]

    yearly_buyout_cost = []
    yearly_leasing_cost = []

    # Antag prisfald på 10% om året
    yearly_price_reduction = 0.9  # TODO: rework til 0.1

    # Antag bilen er købt med et lån på 6% ÅOP
    loan_interest_rate = 0.06

    def __init__(
        self,
        price: int,
        timespan_years: int,
        origin_date: date,
        payout: int,
        monnthly_fee: int,
        decay_price=True,
        new_car=False,
    ):
        """
        :param price: Pris uden moms og afgift i kr
        :param price: Pris inkl. moms og afgift i kr
        :param timespan_years: Tidsperiode bilen skal køres i, i år
        :param origin_date: Bilens 'fødsel'
        :param new_car: Hvorvidt bilen var ny på tidspunket den blev leaset/købt
        """
        # self.price = price * 1.25  # Tilføj moms
        self.price = price
        self.timespan_years = timespan_years
        self.origin_date = origin_date
        self.tax = self.calc_fee()
        self.price_with_taxes = self.calc_buyout()
        self.payout = payout
        self.monthly_fee = monnthly_fee
        self.decay_price = decay_price
        self.calc_lease()

    def calc_buyout(self):
        """Total pris hvis bilen skal købes cash"""
        return self.price + self.tax

    def calc_fee(self) -> int:
        """
        Udregn afgift

        # TODO: Tag højde for små ting, såsom de +/- 5% ved import, m.m.
        https://skat.dk/skat.aspx?oid=2302178


        Fradrag/tillæg til afgiften
        CO2 tillæg 1 afgift - Personbil (125):15.625,00kr.
        CO2 tillæg 2 afgift - Personbil (160):8.750,00kr.
        CO2 tillæg 3 afgift - Personbil (399):113.668,00kr.
        Sum af fradrag/tillæg til afgiften:138.043,00kr.
        """
        total_tax = 0
        remaining_price = self.price

        for fee in self.registration_fees:
            if remaining_price == 0:
                break

            # Håndter billige biler som koster mindre end værdien indenfor satserne
            if remaining_price < fee["amount"]:
                amount = remaining_price
            else:
                amount = fee["amount"]

            remaining_price -= amount
            tax = fee["rate"] * amount
            total_tax += tax
            # print(f'Calculating tax {fee["rate"]=} {amount=} {tax=}')

        return total_tax

    def calc_payout(self):
        """
        Beregn hvad bilen koster årligt, når man har købt bilen i cash

        Prisen inkluderer:
        Værditab, service, renter

        TODO: Service prisen stiger vel fremfor at falde med årene?
        TODO: Skal eventuelt afkast medregnes. Man kunne jo investere pengene fremfor at ligge dem cash i en bil
        """
        car_value = self.price
        remaining_loan = self.price  # Antag at der optages et lån til hele bilen
        total_cost = 0

        for year in range(1, self.timespan_years + 1):
            new_car_value = car_value * self.yearly_price_reduction
            yearly_cost = car_value - new_car_value

            # Antag at service/reparationer årligt udgør 2.5% af bilens værdi
            service_fee = car_value * 0.025

            loan_fee = self.calc_loan_fees()[year]

            print(f"{car_value} {service_fee=} {loan_fee=}")

            yearly_cost += service_fee
            yearly_cost += loan_fee

            car_value = new_car_value
            total_cost += yearly_cost
            self.yearly_buyout_cost.append(
                {
                    "yearly_cost": int(yearly_cost),
                    "price": int(total_cost),
                    "service_fee": int(service_fee),
                    "loan_interest": int(loan_fee),
                    "car_value": int(car_value),
                }
            )

    def calc_lease(self):
        """
        0-3 måneder: 2 % i registreringsafgift
        3-36 måneder: 1 % i registreringsafgift
        +36 måneder: 0,5 % i registreringsafgift
        :return:
        """
        # TODO Amortiseringstabel

        # for year in range(self.timespan):
        #     print(year)

        price = 0
        monthly_fee = self.monthly_fee

        for year in range(1, self.timespan_years + 1):
            # Første år med leasing inkluderer engangsydelse
            if year == 1:
                yearly_cost = int(self.payout + monthly_fee * 12)
            else:
                yearly_cost = int(monthly_fee * 12)

            price += yearly_cost
            monthly_fee = (
                monthly_fee * self.yearly_price_reduction
                if self.decay_price
                else monthly_fee
            )

            self.yearly_leasing_cost.append(
                {
                    "yearly_cost": yearly_cost,
                    "price": price,
                    "payout": self.payout if year == 1 else 0,
                    "monthly_fee": monthly_fee,
                }
            )

    def calc_loan_fees(self):
        """Beregn renter for et givent år"""
        # Antag at der optages et lån til hele bilen
        loan = self.price

        # Afdraget skal justeres til renter.
        # TODO: Kan man beregne denne justering, uden at gennemgå hele lånet?
        loan_interest_fees, _ = self.calc_loan(loan)
        loan += loan_interest_fees

        _, loan_fees_per_year = self.calc_loan(loan)

        return loan_fees_per_year

    def calc_loan(self, remaining_loan):
        """
        TODO: fejl i beregning for eks. Michaels R8
        car = Car(1_700_000, 1, date(2017, 1, 1), 250_000, 15_000, False)
        """

        monthly_interest_rate = self.loan_interest_rate / 12
        loan_monthly_repayment = remaining_loan / self.timespan_years / 12
        print(loan_monthly_repayment)
        loan_fees_per_year = {}

        for year in range(1, self.timespan_years + 1):
            yearly_interest = 0
            for month in range(1, 12 + 1):
                # Afdrager hver måned
                remaining_loan -= loan_monthly_repayment

                # Tilskriver renter hver måned
                monthly_interest = remaining_loan * monthly_interest_rate
                remaining_loan += monthly_interest
                yearly_interest += monthly_interest

                print(f"{int(remaining_loan)=} {int(monthly_interest)}")
            loan_fees_per_year[year] = yearly_interest

        return remaining_loan, loan_fees_per_year

    def table(self):
        print("Leasing prices:")
        print(
            f'{"Year":<10} {"Price/year":<20} {"Payout":<20} {"Yearly fee":<20} {"Total price":<20}'
        )
        for idx, prices in enumerate(self.yearly_leasing_cost):
            print(
                f'{idx + 1:<10} {prices["yearly_cost"]:<20} {prices["payout"]:<20} {prices["monthly_fee"]*12:<20} {prices["price"]:<20}'
            )

        print("Buyout prices:")
        print(
            f'{"Year":<10} {"Price/year":<20} {"Service fee":<20} {"Loan interest":<20} {"Car value":<20} {"Total price":<20}'
        )
        for idx, prices in enumerate(self.yearly_buyout_cost):
            print(
                f'{idx + 1:<10} {prices["yearly_cost"]:<20} {prices["service_fee"]:<20} {prices["loan_interest"]:<20} {prices["car_value"]:<20} {prices["price"]:<20}'
            )

    def graph(self):
        plt.xlabel("År")
        plt.ylabel("Pris")

        # Leasing
        # År 0 koster det 0 kr. Indtaster dette år for at grafen også tegnes for leasing over blot 1 år
        x1 = [0] + [num for num in range(1, self.timespan_years + 1)]
        y1 = [0] + [price["price"] for price in self.yearly_leasing_cost]
        plt.plot(x1, y1, label="Leasing")

        # Køb
        x2 = [0] + [num for num in range(1, self.timespan_years + 1)]
        y2 = [0] + [price["price"] for price in self.yearly_buyout_cost]
        plt.plot(x2, y2, label="Køb")

        plt.legend()
        plt.savefig("fig.png")
        # plt.show()


car = Car(1_700_000, 1, date(2017, 1, 1), 250_000, 15_000, False)
car.calc_buyout()
car.calc_payout()
car.table()
car.graph()
