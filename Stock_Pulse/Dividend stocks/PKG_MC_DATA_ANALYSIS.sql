CREATE OR REPLACE PACKAGE pkg_mc_data_analysis AS
    PROCEDURE prc_perform_calc (
        p_err      OUT NUMBER,
        p_err_desc OUT VARCHAR2
    );

    PROCEDURE prc_div_stocks (
        p_err      OUT NUMBER,
        p_err_desc OUT VARCHAR2
    );

END pkg_mc_data_analysis;

/

CREATE OR REPLACE PACKAGE BODY pkg_mc_data_analysis AS

    PROCEDURE prc_perform_calc (
        p_err      OUT NUMBER,
        p_err_desc OUT VARCHAR2
    ) AS
        v_calc_avg   VARCHAR2(20);
        string_1     VARCHAR2(4000);
        result_value VARCHAR2(20);
    BEGIN
        DELETE FROM mc_calc_weightage;

        COMMIT;
        INSERT INTO mc_calc_weightage ( stock_name )
            SELECT DISTINCT
                stock_name
            FROM
                nse_stock_list;

        COMMIT;

------ Perform calculate and add weightage
--Find Average
        SELECT
            round(AVG(ttm_eps))
        INTO v_calc_avg
        FROM
            (
                SELECT
                    ttm_eps
                FROM
                    nse_stock_list
                ORDER BY
                    ttm_eps DESC
            )
        WHERE
            ROWNUM <= (
                SELECT
                    round(((max_value + min_value) / 2)) AS value
                FROM
                    mc_calc_config
                WHERE
                    parameter_name = 'STOCK_SELECTION'
            );

        FOR stock IN (
            SELECT
                stock_name,
                ttm_eps
            FROM
                (
                    SELECT
                        stock_name,
                        ttm_eps,
                        length(ttm_eps)
                    FROM
                        nse_stock_list
                    ORDER BY
                        ttm_eps DESC
                )
            WHERE
                ROWNUM <= (
                    SELECT
                        round(((max_value + min_value) / 2)) AS value
                    FROM
                        mc_calc_config
                    WHERE
                        parameter_name = 'STOCK_SELECTION'
                )
        ) LOOP
            IF stock.ttm_eps >= v_calc_avg THEN
                UPDATE mc_calc_weightage
                SET
                    weightage = nvl(weightage, 0) + 1
                WHERE
                    stock_name = stock.stock_name;

            END IF;
        END LOOP;   --End
    END prc_perform_calc;

    -- pakcage called only for the Dividend stock update------

    PROCEDURE prc_div_stocks (
        p_err      OUT NUMBER,
        p_err_desc OUT VARCHAR2
    ) AS
    BEGIN

-- Inserting new entries from the daily job into config
        INSERT INTO dividend_stocks_config (
            company_name,
            new_entry,
            announcement_date,
            record_date,
            created_date,
            modified_date
        )
            SELECT
                company_name,
                'Y',
                announcement_date,
                record_date,
                sysdate,
                sysdate
            FROM
                dividend_stocks ds
            WHERE
                    trunc(created_date) = trunc(sysdate)
                AND NOT EXISTS (
                    SELECT
                        1
                    FROM
                        dividend_stocks_config con
                    WHERE
                        con.company_name = ds.company_name and trunc(created_date) >= trunc(sysdate) - 90   ---- Checking with last 3 month records
                );

        COMMIT;

--Update every time  EXPIRED = 'YES' 
        UPDATE dividend_stocks_config co
        SET
            expired = 'YES'
        WHERE
            EXISTS (
                SELECT
                    1
                FROM
                    dividend_stocks ds
                WHERE
                        ds.company_name = co.company_name
                    AND trunc(record_date) <= trunc(sysdate)
            );

--Create ID at first for all the entries
        UPDATE dividend_stocks
        SET
            announcement_id = dbms_utility.get_hash_value(company_name, 0, power(2, 20))
                              || dbms_utility.get_hash_value(announcement_date, 0, power(2, 20))
        WHERE
            announcement_id IS NULL;

        UPDATE dividend_stocks
        SET
            record_id = dbms_utility.get_hash_value(company_name, 0, power(2, 20))
                        || dbms_utility.get_hash_value(record_date, 0, power(2, 20))
        WHERE
            record_id IS NULL;

-- update ANNOUNCEMENT_DATE value for the existing stock into DIVIDEND_STOCKS_CONFIG
        FOR i IN (
            SELECT
                company_name,
                announcement_date,
                announcement_id
            FROM
                dividend_stocks
        ) LOOP
            UPDATE dividend_stocks_config con
            SET
                announcement_date = i.announcement_date,
                modified_date = sysdate
            WHERE
                    con.company_name = i.company_name
                AND trunc(announcement_date) <> trunc(i.announcement_date)
                AND announcement_id = i.announcement_id;

        END LOOP;

-- update RECORD_DATE value for the existing stock
        FOR i IN (
            SELECT
                company_name,
                record_date,
                record_id
            FROM
                dividend_stocks
        ) LOOP
            UPDATE dividend_stocks_config con
            SET
                record_date = i.record_date,
                record_dt_change_date = sysdate
            WHERE
                    con.company_name = i.company_name
                AND trunc(record_date) <> trunc(i.record_date)
                AND record_id = i.record_id;

        END LOOP;

    END prc_div_stocks;

END pkg_mc_data_analysis;

/


