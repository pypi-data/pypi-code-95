from typing import Optional, List, Union
from pydantic import BaseModel, Field
from datetime import date, datetime


class Company(BaseModel):
    code: str
    name: str


class Center(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None


class ExpiringCenter(BaseModel):
    center: Center
    dueDate: Optional[Union[date, datetime]]

    class Config:
        json_encoders = {
            date: lambda v: v.strftime("%Y%m%d"),
            datetime: lambda v: v.strftime("%Y%m%d%H%M%S")
        }


class Card(BaseModel):
    number: str


class CardList(BaseModel):
    cards: List[Card]
    required: Optional[bool] = False


class OptionalData(BaseModel):
    level: int
    value: str


class Department(BaseModel):
    # TODO: Change this
    path: Optional[str] = Field(
        default=None,
        title="Department path",
        description="""
            Can be like SPEC/AR/IT.
            Use 'sep_in' param if you need change the splitted character.
        """
    )
    sep_in: Optional[str] = '/'
    sep_out: Optional[str] = ';'
    levels: Optional[Union[dict, list, tuple, set]] = Field(
        default=None,
        title="Department levels",
        description="""
            Can be like a dict or iterable item. E.g.
            {"1": "SPEC", "2": "AR", "3": "IT"}
            ["SPEC", "AR", "IT"]
            ...
        """
    )


class Employee(BaseModel):
    nif: str
    enrollment: Optional[str] = None
    code: Optional[int] = None
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    comment: Optional[str] = None
    company: Optional[Company] = None
    center: Optional[Center] = None
    expCenters: Optional[List[ExpiringCenter]] = None
    cardList: Optional[CardList] = None
    optionalData: Optional[List[OptionalData]] = None
    department: Optional[Department] = None

    def get_cardList(self) -> dict:
        return {
            "cards": ','.join([str(c_.number) for c_ in self.cardList.cards]),
            "cardRequired": self.cardList.required
        } if self.cardList else {}

    def get_company(self) -> dict:
        return {
            "companyCode": self.company.code,
            "companyName": self.company.name
        } if self.company else {}
    
    def get_center(self) -> dict:
        if not self.center:
            return {}

        if self.center.code:
            return {"centerCode": self.center.code}
        
        return {"centerName": self.center.name}

    def get_expCenters(self) -> dict:
        if not self.expCenters:
            return {}

        return {
            "centers": ','.join([
                '{}:{}'.format(
                   ec.center.code,
                    ec.dueDate.strftime("%Y%m%d")
                ) for ec in self.expCenters
            ])
        }

    def get_optionalData(self) -> dict:
        return {
            "optionalData": ','.join([
                '{}:{}'.format(
                    od.level,
                    od.value
                ) for od in self.optionalData
            ])
        } if self.optionalData else {}

    def get_department(self) -> dict:
        if not self.department:
            return {}
        # depart path like SPEC/AR/IT/ID
        if self.department.path:
            return {
                "departPath": self.department.path.replace(
                    self.department.sep_in,
                    self.department.sep_out
                )
            }
        # have not path or levels
        if not self.department.levels:
            return {}

        # can be like {"1": "SPEC", }
        if isinstance(self.department.levels, dict):
            return {
                f'departLvl{k}': v for k,v in self.department.levels.items()
            }

        if isinstance(self.department.levels, (list, tuple, set)):
            return {
                f'departLvl{i+1}': self.department.levels[i]
                for i in range(len(self.department.levels))
            }


    class Config:
        json_encoders = {
            date: lambda v: v.strftime("%Y%m%d"),
            datetime: lambda v: v.strftime("%Y%m%d%H%M%S")
        }
    
    class Meta:
        nondefault: set = {
            'cardList',
            'company',
            'center',
            'expCenters', 
            'optionalData',
            'department'
        }
