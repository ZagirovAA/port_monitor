#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from easysnmp import Session
from ipaddress import ip_address

class Device:
    """ Класс для создания объектов устройств типа свич или роутер """

    # Если явно не задано имя устройства, оно будет генерироваться
    # динамически из имени по-умолчанию и порядкового номера
    number = 0
    # Коэффициент скорости порта. Для примера при скорости порта 10 мб/с,
    # по снмп возвращается значение 10000000, то есть скорость кратная 1000000
    coefficient = 1000000
    # Значения по-умолчанию для атрибутов объекта
    DFL_NAME = "device"
    DFL_ADDRESS = "127.0.0.1"
    DFL_COMMUNITY = "public"
    DFL_VERSION = "2"
    # Версии снмп для сверки на корректность ввода
    VERSIONS = ("1", "2", "3")
    # OID для получения количества интерфейсов
    IF_COUNT = "1.3.6.1.2.1.2.1.0"
    # OID для получения номеров интерфейсов
    IF_INDEX = "1.3.6.1.2.1.2.2.1.1"
    # OID для получения типа интерфейса
    IF_TYPE = "1.3.6.1.2.1.2.2.1.3."
    # OID для получения скорости заданного интерфейса
    IF_SPEED = "1.3.6.1.2.1.2.2.1.5."
    # OID для получения количества принятых байт на интерфейсе
    IF_IN_OCTETS = "1.3.6.1.2.1.2.2.1.10."
    # OID для получения количества отправленных байт на интерфейсе
    IF_OUT_OCTETS = "1.3.6.1.2.1.2.2.1.16."

    def __init__(self,
                 address="127.0.0.1",
                 community="public",
                 version="2",
                 name="device"):
        """ Конструктор принимает минимум параметров
        для соединения с устройством по снмп """

        # Инкремент номера устройства для динамической
        # генерации имени по необходимости
        Device.number += 1
        # Если параметры состоят только из пробелов и прочих
        # разделителей, то конструктор будет использовать
        # значения по-умолчанию для переданных параметров
        address = address.strip()
        community = community.strip()
        name = name.strip()
        # Адрес должен быть задан и соответствовать формату ip
        if not address or not Device.__is_ip_address(address):
            address = Device.DFL_ADDRESS
        self.__address = address
        # Комьюнити не должно быть пустым
        if not community:
            community = Device.DFL_COMMUNITY
        self.__community = community
        # Версия должна быть указана и соответствовать
        # одной из предопределенных
        if not version or version not in Device.VERSIONS:
            version = Device.DFL_VERSION
        self.__version = version
        # Если имя устройства не задано или используется имя по-умолчанияю,
        # то будет использоваться динамическое
        # имя на основе порядкового номера устройства
        if not name or name == "device":
            name = Device.DFL_NAME + str(Device.number)
        self.__name = name
        # Атрибут со ссылкой на созданную с устройством сессию
        self.__session = None
        # Количесто интерфейсов у устройства
        self.__count = 0
        # Список интерфейсов устройства
        self.__ports = []
        # Количество интерфейсов у устройства
        self.__interfaces_count = 0
        # Список номеров интерфейсов
        self.__interfaces_numbers = []

    def __str__(self):
        """ Вывод на экран имени, адреса, комьюнити и версии устройства """

        return "Name: {0} Address: {1} Community: {2} Version: {3}".format(
            self.__name,
            self.__address,
            self.__community,
            self.__version)

    # -------------------------------------
    # Раздел объявления свойств и сеттеров
    # -------------------------------------
    @property
    def device_name(self):
        return self.__name

    @device_name.setter
    def device_name(self, new_value):
        if type(new_value) == str:
            new_value.strip()
            if new_value:
                self.__name = new_value
            else:
                print("Свойству name нельзя назначать пустое значение.")
        else:
            print("Свойству name можно присваивать только текстовые значения.")

    @property
    def device_address(self):
        return self.__address

    @device_address.setter
    def device_address(self, new_value):
        if type(new_value) == str:
            new_value.strip()
            if new_value and Device.__is_ip_address(new_value):
                self.__address = new_value
            else:
                print("Свойству address нельзя назначать пустое значение, "
                      "либо значение, не соответствующее формату ip адреса.")
        else:
            print("Свойству address можно присваивать "
                  "только текстовые значения.")

    @property
    def snmp_community(self):
        return self.__community

    @snmp_community.setter
    def snmp_community(self, new_value):
        if type(new_value) == str:
            new_value.strip()
            if new_value:
                self.__community = new_value
            else:
                print("Свойству community нельзя назначать пустое значение.")
        else:
            print("Свойству community можно присваивать "
                  "только текстовые значения.")

    @property
    def snmp_version(self):
        return self.__version

    @snmp_version.setter
    def snmp_version(self, new_value):
        if new_value and new_value in Device.VERSIONS:
            self.__version = new_value
        else:
            print("В качестве значения свойства version "
                  "может быть только число в диапозоне от 1 до 3.")

    @property
    def interfaces_count(self):
        return self.__interfaces_count

    @property
    def interfaces_numbers(self):
        return self.__interfaces_numbers

    # -------------------------------------
    # Раздел объявления публичных методов
    # -------------------------------------
    def connect_device(self):
        try:
            self.__session = Session(hostname=self.__address,
                                     community=self.__community,
                                     version=int(self.__version))
            self.__interfaces_count = Device.__get_interfaces_count(self.__session)
            self.__interfaces_numbers = Device.__get_interfaces_numbers(self.__session)
            return True
        except Exception:
            print("Не удалось осуществить соединение с сетевым устройством. "
                  "Возможно устройство не доступно, либо "
                  "параметры подключения заданы не верно.")
            return False

    def get_interface_type(self, port):
        """ Возвращает тип заданного интерфейса """

        port_type = 0
        if self.interfaces_count > 0 and port in self.interfaces_numbers:
            try:
                snmp_data = str(self.__session.get(Device.IF_TYPE + str(port)))
            except Exception:
                print("Не удалось получить тип интерфейса.")
                return port_type
            interface_value = Device.__parse_value(snmp_data)
            if interface_value.isdigit():
                port_type = int(interface_value)
            else:
                print("Тип интерфейса должен быть в числовом формате.")
        else:
            print("Нет доступных интерфейсов, либо номер "
                  "интерфейса указан не верно.")
        return port_type

    def get_interface_speed(self, port):
        """ Возвращает скорость заданного интерфейса """

        port_speed = 0
        if self.interfaces_count > 0 and port in self.interfaces_numbers:
            try:
                snmp_data = str(self.__session.get(Device.IF_SPEED + str(port)))
            except Exception:
                print("Не удалось получить скорость интерфейса.")
                return port_speed
            interface_value = Device.__parse_value(snmp_data)
            if interface_value.isdigit():
                interface_value = int(interface_value)
                if interface_value > Device.coefficient:
                    port_speed = interface_value / Device.coefficient
            else:
                print("Номер интерфейса должен быть в числовом формате.")
        else:
            print("Нет доступных интерфейсов, либо "
                  "номер интерфейса указан не верно.")
        return port_speed

    def get_input_bandwidth(self, port):
        """ Возвращает количество принятых байт на интерфейсе """

        port_bandwidth = 0
        if self.interfaces_count > 0 and port in self.interfaces_numbers:
            try:
                snmp_data = str(self.__session.get(
                    Device.IF_IN_OCTETS + str(port)))
            except Exception:
                print("Не удалось получить количество входящих байт.")
                return port_bandwidth
            interface_value = Device.__parse_value(snmp_data)
            if interface_value.isdigit():
                port_bandwidth = int(interface_value)
            else:
                print("Количество входящих байт должно "
                      "быть в числовом формате.")
        else:
            print("Нет доступных портов, либо номер порта указан не верно.")
        return port_bandwidth

    def get_output_bandwidth(self, port):
        """ Возвращает количество отправленных байт на интерфейсе """

        port_bandwidth = 0
        if self.interfaces_count > 0 and port in self.interfaces_numbers:
            try:
                snmp_data = str(self.__session.get(
                    Device.IF_OUT_OCTETS + str(port)))
            except Exception:
                print("Не удалось получить количество исходящих байт.")
                return port_bandwidth
            interface_value = Device.__parse_value(snmp_data)
            if interface_value.isdigit():
                port_bandwidth = int(interface_value)
            else:
                print("Количество исходящих байт должно "
                      "быть в числовом формате.")
        else:
            print("Нет доступных портов, либо номер порта указан не верно.")
        return port_bandwidth

    # -------------------------------------
    # Раздел объявления приватных методов
    # -------------------------------------
    @staticmethod
    def __parse_value(value):
        """ Возвращает значение из строки снмп формата """

        interface_value = ""
        if type(value) == str:
            # На случай, если значение состоит только из разделителей
            value.strip()
            if value:
                interface_value = value.split(" ")
                if len(interface_value) > 0:
                    # Необходимо из строки value='data' получить только data.
                    # Чтобы получить срез строки нужна стартовая позиция и
                    # длина полезной строки, которую можно получить, минусовав
                    # из длины всей строки лишние 8 символов. Стартовая
                    # позиция 7, а конечная - длина полезной строки плюс 7.
                    interface_value = interface_value[1]
                    interface_value = interface_value[7:(len(interface_value) - 8) + 7]
                else:
                    print("Данные, подлежащие парсингу, должны состоять "
                          "из нескольких слов, разделенных пробелами.")
            else:
                print("Данные, подлежащие парсингу, не должны быть пустыми.")
        else:
            print("Данные, подлежащие парсингу, должны "
                  "быть в текстовом формате.")
        return interface_value

    @staticmethod
    def __get_interfaces_count(session):
        """ Возвращает количество доступных интерфейсов """

        interfaces_count = 0
        try:
            snmp_data = str(session.get(Device.IF_COUNT))
        except Exception:
            print("Не удалось получить количество интерфейсов.")
            return interfaces_count
        count = Device.__parse_value(snmp_data)
        if count.isdigit():
            interfaces_count = int(count)
        else:
            print("Количество портов должно быть числовым значением.")
        return interfaces_count

    @staticmethod
    def __get_interfaces_numbers(session):
        """ Возвращает список номеров интерфейсов """

        interfaces_numbers = []
        try:
            index = session.walk(Device.IF_INDEX)
        except Exception:
            print("Не удалось получить список номеров интерфейсов.")
            return interfaces_numbers
        index_count = len(index)
        if index_count > 0:
            for interface in index:
                interface = str(interface)
                interfaces_numbers.append(int(Device.__parse_value(interface)))
        else:
            print("Количество номеров интерфейсов должно быть больше нуля.")
        return interfaces_numbers

    @staticmethod
    def __is_ip_address(address):
        try:
            ip_address(address)
            return True
        except:
            return False