from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class Dormitory(Base):
    """
    Модель "Общежитие"
    """
    __tablename__ = 'platonus_univer_dormitories'

    # Идентификатор
    id = Column('dormitoryID', Integer, primary_key=True)

    # Адрес общежития
    address = Column(String(256))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<Dormitory {} (id={} status={})>'.format(self, self.id, self.status)
    
    def __str__(self):
        return self.address


class DormitoryRoom(Base):
    """
    Модель "Комната общежития"
    """
    __tablename__ = 'univer_dormitory_rooms'

    # Идентификатор
    id = Column('dormitory_room_id', Integer, primary_key=True)

    # Общежитие
    dormitory_id = Column(ForeignKey('platonus_univer_dormitories.dormitoryID'))
    dormitory = relationship('Dormitory')

    # Этаж
    floor = Column('dormitory_room_floor', Integer)

    # Вместимость
    size = Column('dormitory_room_size', Integer)

    # Наименование
    number_ru = Column('dormitory_room_number_ru', String(30))
    number_kz = Column('dormitory_room_number_kz', String(30))
    number_en = Column('dormitory_room_number_en', String(30))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<DormitoryRoom {} (id={} dormitory_id={} floor={} size={} status={}>'.format(self, self.id, self.dormitory_id, self.floor, self.size, self.status)
    
    def __str__(self):
        return self.number_ru


class DormitoryApplicant(Base):
    """
    Модель "Заявление общежития"
    """
    __tablename__ = 'univer_dormitory_applicant'

    # Идентификатор
    id = Column('dormitory_applicant_id', Integer, primary_key=True)

    # Дата и время создания заявления
    dormitory_applicant_create = Column(DateTime)

    # Факультет
    faculty_id = Column(ForeignKey('univer_faculty.faculty_id'))
    faculty = relationship('Faculty')

    # Общежитие
    dormitory_id = Column(ForeignKey('platonus_univer_dormitories.dormitoryID'))
    dormitory = relationship('Dormitory')

    # Статус заявления
    dormitory_applicant_status = Column(Integer)

    # Статус
    status = Column(Integer)

    # Год
    year = Column(Integer)

    def __repr__(self):
        return '<DormitoryApplicant {} (id={})>'.format(self, self.id)
    
    def __str__(self):
        return str(self.dormitory_applicant_create)


class DormitoryApplicantStudent(Base):
    """
    Модель "Студент в заявке общежития"
    """
    __tablename__ = 'univer_dormitory_applicant_students'

    # Заявление общежития
    dormitory_applicant_id = Column(ForeignKey('univer_dormitory_applicant.dormitory_applicant_id'), primary_key=True)
    dormitory_applicant = relationship('DormitoryApplicant')

    # Студент
    student_id = Column(ForeignKey('univer_students.students_id'), primary_key=True)
    student = relationship('Student')

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<DormitoryApplicantStudent {} (dormitory_applicant_id={})>'.format(self, self.dormitory_applicant_id)
    
    def __str__(self):
        return str(self.student)


class StudentDormitoryRoomLink(Base):
    """
    Модель "Связь между студентом и комнатой"
    """
    __tablename__ = 'univer_student_dormitory_room_link'

    # Студент
    student_id = Column(ForeignKey('univer_students.students_id'), primary_key=True)
    student = relationship('Student')

    # Комната общежития
    dormitory_room_id = Column(ForeignKey('univer_dormitory_rooms.dormitory_room_id'), primary_key=True)
    dormitory_room = relationship('DormitoryRoom')

    # Год
    year = Column(Integer)

    # Дата и время создания
    created = Column(DateTime)

    # Заявление общежития
    dormitory_applicant_id = Column(ForeignKey('univer_dormitory_applicant.dormitory_applicant_id'))
    dormitory_applicant = relationship('DormitoryApplicant')

    def __repr__(self):
        return '<StudentDormitoryRoomLink {} (dormitory_applicant_id={})>'.format(self, self.dormitory_applicant_id)
    
    def __str__(self):
        return '{} - {}'.format(self.student, self.dormitory_room)


class StudentDormitoryRoomSettleHistory(Base):
    """
    Модель "История проживания в комнате общежития студентом"
    """
    __tablename__ = 'univer_student_dormitory_room_settle_history'

    # Идентификатор
    id = Column('history_id', Integer, primary_key=True)

    # Студент
    student_id = Column(ForeignKey('univer_students.students_id'))
    student = relationship('Student')

    # Комната общежития
    dormitory_room_id = Column(ForeignKey('univer_dormitory_rooms.dormitory_room_id'))
    dormitory_room = relationship('DormitoryRoom')

    # Дата и время
    date = Column('history_date', DateTime)

    # Заявление общежития
    dormitory_applicant_id = Column(ForeignKey('univer_dormitory_applicant.dormitory_applicant_id'))
    dormitory_applicant = relationship('DormitoryApplicant')

    # Общежитие
    dormitory_id = Column(ForeignKey('platonus_univer_dormitories.dormitoryID'))
    dormitory = relationship('Dormitory')

    # Тип приказа
    order_type = Column(Integer)

    # Дата и время приказа
    order_date = Column(DateTime)

    # Статус приказа
    order_status = Column(Integer)

    def __repr__(self):
        return '<StudentDormitoryRoomSettleHistory {} (id={} student_id={} dormitory_room_id={} date={} dormitory_applicant_id={} order_type={}'.format(
            self,
            self.id,
            self.student_id,
            self.dormitory_room_id,
            self.date,
            self.dormitory_applicant_id,
            self.order_type
        )

    def __str__(self):
        return str(self.student)