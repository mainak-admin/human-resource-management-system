SELECT * FROM hrmsdb.dependent;




CREATE VIEW hrmsdb.dependent_details_table AS
SELECT hrmsdb.dependent.DEPENDENT_ID, hrmsdb.dependent.EMP_ID, hrmsdb.dependent.FIRST_NAME,
hrmsdb.dependent.LAST_NAME, hrmsdb.dependent.RELATION, hrmsdb.dependent.DATE_OF_BIRTH, hrmsdb.dependent.PHONE_NUMBER,
hrmsdb.dependent.EMAIL, hrmsdb.dependent_address.HOUSE_NO, hrmsdb.dependent_address.ADDRESS_LINE,
hrmsdb.dependent_address.AREA, hrmsdb.dependent_address.CITY, hrmsdb.dependent_address.STATE,
hrmsdb.dependent_address.COUNTRY, hrmsdb.dependent_address.PINCODE FROM hrmsdb.dependent JOIN
hrmsdb.dependent_address ON hrmsdb.dependent.DEPENDENT_ID = hrmsdb.dependent_address.DEPENDENT_ID;

SELECT * FROM hrmsdb.dependent_details_table;
