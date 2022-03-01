import re
from datetime import date
from typing import Dict
from typing import Any

# Pydantic
from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr
from pydantic import PaymentCardNumber
from pydantic.validators import str_validator
from pydantic.types import PaymentCardBrand

# Fast API
from fastapi import FastAPI
from fastapi import Body


app = FastAPI()

PHONE_REGEXP = re.compile(r'^\+?[0-9]{1,3}?[0-9]{6,14}$')

# Custom Types


class PhoneNumber(str):
    """Phone number type"""

    @classmethod
    def __get_validators__(cls) -> Dict[str, Any]:
        yield str_validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(
            pattern=r'^\+?[0-9]+$',
            example=['+541112345678'],
            format='phone-number',
        )

    @classmethod
    def validate(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError('Phone number must be a string')

        match = PHONE_REGEXP.search(value)

        if not match:
            raise ValueError('Phone number must be a valid phone number')

        return value

    def __repr__(self) -> str:
        return f'PhoneNumber({super().__repr__()})'


# Models


class Person(BaseModel):
    name: str = Field(...,
                      min_length=2,
                      max_length=50,
                      title='Name',
                      description='The name of the person that will receive the package.',
                      example='John Doe')

    email: EmailStr = Field(...,
                            title='Email',
                            description='The email of the person that will receive the package.')

    phone: PhoneNumber = Field(...,
                               title='Phone',
                               description='The phone number of the person that will receive the package.')


class Product(BaseModel):
    """Product model"""

    name: str = Field(...,
                      min_length=2,
                      max_length=50,
                      title='Name',
                      description='The name of the product.',
                      example='Laptop')


class  PaymentMethod(BaseModel):
    """Payment method model"""

    card_number: PaymentCardNumber = Field(...,
                                      title='Number',
                                      description='The number of the payment card.',
                                      example='1234567890123456')

    expiration_month: int = Field(...,
                                  title='Expiration month',
                                  description='The expiration month of the payment card.',
                                  ge=1,
                                  le=12,
                                  example=12)

    expiration_year: int = Field(...,
                                 title='Expiration year',
                                 description='The expiration year of the payment card.')

    @property
    def brand(self) -> PaymentCardBrand:
        """Returns the brand of the payment card"""
        return self.card_number.brand

    @property
    def expired(self) -> bool:
        """Returns if the payment card is expired"""

        today = date.today()
        expiration_date = date(year=self.expiration_year,
                               month=self.expiration_month,
                               day=1)

        return today > expiration_date


class Address(BaseModel):
    """Address model"""

    street: str = Field(...,
                        min_length=2,
                        max_length=50,
                        title='Street',
                        description='The street of the address.')

    city: str = Field(...,
                      min_length=2,
                      max_length=50,
                      title='City',
                      description='The city of the address.')

    country: str = Field(...,
                         min_length=2,
                         max_length=50,
                         title='Country',
                         description='The country of the address.')

# Endpoints

@app.post('/order')
def add_order(
    person: Person = Body(...,),
    product: Product = Body(...,),
    address: Address = Body(...,),
    payment_method: PaymentMethod = Body(...,),
):
    """Registers a new order"""

    return {
        'person': person,
        'product': product,
        'address': address,
        'payment_method': {
            'brand': payment_method.brand,
            'last4': payment_method.card_number.last4,
            'mask': payment_method.card_number.masked,
            'expired': payment_method.expired,
        }
    }
