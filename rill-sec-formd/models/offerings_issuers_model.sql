-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true

SELECT
  SALE_DATE AS offering_saledate, 
  INDUSTRYGROUPTYPE AS offering_IndustryGroupType,
  INVESTMENTFUNDTYPE AS offering_InvestmentFundType, 
  ISSUERS.ENTITYNAME AS issuer_EntityName, 
  RECIPIENTS.RECIPIENTNAME AS recipient_name,
   CAST(
    CASE 
      WHEN TOTALOFFERINGAMOUNT == 'Indefinite' THEN 0
      ELSE TOTALOFFERINGAMOUNT 
     END
    AS BIGINT) AS TotalOfferingAmount, 
  *
FROM 
   OFFERINGS 
   LEFT JOIN ISSUERS ON OFFERINGS.ACCESSIONNUMBER = ISSUERS.ACCESSIONNUMBER
   LEFT JOIN RECIPIENTS ON OFFERINGS.ACCESSIONNUMBER = RECIPIENTS.ACCESSIONNUMBER
WHERE SALE_DATE BETWEEN DATE '2020-01-01' AND current_date()  

ORDER BY SALE_DATE DESC