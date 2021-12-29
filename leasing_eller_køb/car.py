from datetime import date


class Car:

    """
    Se afgifts satser:
    https://skat.dk/SKAT.aspx?oid=2234529
    """
    registration_fees = [
        {
            "rate": 0.25,
            "amount": 65000
        },
        {
            "rate": 0.85,
            "amount": 137200
        },
        {
            "rate": 1.50,
            "amount": 999999999  # Resten af bilens værdi
        }
    ]

    def __init__(self, price: int, timespan: int, origin_date: date):
        """
        :param price: Pris uden moms og afgift i kr
        :param timespan: Tidsperiode bilen skal køres i, i år
        :param origin_date: Bilens 'fødsel'
        """
        self.price = price * 1.25  # Tilføj moms
        self.timespan = timespan
        self.origin_date = origin_date
        self.tax = self.calc_fee()
        self.price_with_taxes = self.calc_buyout()
        # print(f'{self.price_with_taxes=} {self.price=} {self.tax=}')
        self.calc_lease()

    def calc_buyout(self):
        """ Total pris hvis bilen skal købes cash """
        return self.price + self.tax

    def calc_fee(self) -> int:
        """ Udregn afgift

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

    def calc_lease(self):
        """
        0-3 måneder: 2 % i registreringsafgift
        3-36 måneder: 1 % i registreringsafgift
        +36 måneder: 0,5 % i registreringsafgift
        :return:
        """
        print(f'Amortiseringstabel TODO')

        for year in range(self.timespan):
            print(year)


car = Car(560000, 1, date(2017, 1, 1))
car.calc_buyout()

