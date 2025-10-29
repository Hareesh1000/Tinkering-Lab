create or replace package  PKG_STOCK_PULSE_ANALYSE
as
procedure PRC_SP_FIBO_ANALYS (p_err out number , p_err_desc out varchar2 ); -- Procedure for FIBO analysis of stock from MC data.
procedure PRC_SP_TICKER_DATA_ANALYSE (p_err out number , p_err_desc out varchar2 ); -- Procedure to analyse the ticker data from TickerTape

end PKG_STOCK_PULSE_ANALYSE;

/

CREATE OR REPLACE PACKAGE BODY PKG_STOCK_PULSE_ANALYSE AS

    /* ========================================================================================
       Procedure: PRC_SP_FIBO_ANALYS
       Purpose  : Performs Fibonacci analysis on stock prices.
                   - Refreshes SP_STOCK_ANALYSIS table
                   - Updates high/low levels
                   - Calculates Fibonacci retracement levels
       ======================================================================================== */
    PROCEDURE PRC_SP_FIBO_ANALYS (p_err OUT NUMBER, p_err_desc OUT VARCHAR2)
    AS
        price_move      NUMBER;
        starting_price  NUMBER;
        ending_price    NUMBER;
    BEGIN
        p_err := 0;

        -- Step 1: Clean the target table before inserting
        DELETE FROM SP_STOCK_ANALYSIS;

        -- Step 2: Insert current stock details
        INSERT INTO SP_STOCK_ANALYSIS (STOCK_NAME, LTP, HIGH_52_WEEKS, LOW_52_WEEKS)
        SELECT STOCK_NAME, PREVIOUS_CLOSE, HIGH_52_WEEKS, LOW_52_WEEKS
        FROM NSE_STOCK_LIST;

        -- Step 3: Update each stock’s historical high and low from NSE_STOCK_HISTORY
        UPDATE SP_STOCK_ANALYSIS sp
        SET 
            HIGH = (SELECT MAX(PREVIOUS_CLOSE) 
                    FROM NSE_STOCK_HISTORY 
                    WHERE STOCK_NAME = sp.STOCK_NAME),
            LOW = (SELECT MIN(PREVIOUS_CLOSE) 
                   FROM NSE_STOCK_HISTORY 
                   WHERE STOCK_NAME = sp.STOCK_NAME);

        COMMIT;

        -- Step 4: Update stock trend status based on various price comparisons
        UPDATE SP_STOCK_ANALYSIS sp
        SET STATUS = CASE 
                        WHEN sp.LTP >= sp.HIGH THEN 'MOVING'
                        WHEN sp.LTP <= sp.HIGH THEN 'BELOW LAST HIGH'
                        WHEN sp.LTP >= sp.HIGH_52_WEEKS THEN 'TRENDING - ABOVE 52W'
                        WHEN sp.LTP <= sp.LOW_52_WEEKS THEN 'FALLING - BELOW 52W'
                        ELSE NULL
                     END;

        COMMIT;

        -- Step 5: Loop through each record and compute Fibonacci retracement levels
        FOR i IN (SELECT * FROM SP_STOCK_ANALYSIS)
        LOOP
            starting_price := i.LOW_52_WEEKS;
            ending_price   := i.HIGH_52_WEEKS;

            price_move := ending_price - starting_price;

            UPDATE SP_STOCK_ANALYSIS sp
            SET
                FIBO_LEVEL_1 = starting_price + 0.236 * price_move,
                FIBO_LEVEL_2 = starting_price + 0.382 * price_move,
                FIBO_LEVEL_3 = starting_price + 0.500 * price_move,
                FIBO_LEVEL_4 = starting_price + 0.618 * price_move,
                FIBO_LEVEL_5 = starting_price + 0.786 * price_move
            WHERE STOCK_NAME = i.STOCK_NAME;
        END LOOP;

        COMMIT;

        -- Step 6: Return success message
        p_err := SQLCODE;
        IF p_err = 0 THEN
            p_err_desc := 'Success';
        ELSE
            p_err_desc := 'Exception occurred: ' || SQLERRM;
        END IF;

    EXCEPTION
        WHEN OTHERS THEN
            p_err := SQLCODE;
            p_err_desc := 'Exception in PRC_SP_FIBO_ANALYS: ' || SQLERRM;
    END PRC_SP_FIBO_ANALYS;

    /* ========================================================================================
       Procedure: PRC_SP_TICKER_DATA_ANALYSE
       Purpose  : Analyzes ticker tape raw data to extract stock performance attributes.
                  - Extracts performance, valuation, growth, etc.
                  - Updates SP_STOCK_TICKER_ANALYSIS table dynamically
       ======================================================================================== */
    -- PROCEDURE PRC_SP_TICKER_DATA_ANALYSE (p_err OUT NUMBER, p_err_desc OUT VARCHAR2)
    -- AS
    --     price_move          NUMBER;
    --     starting_price      NUMBER;
    --     ending_price        NUMBER;
    --     cnt                 NUMBER := 0;
    --     attribs             VARCHAR2(30);

    --     v_update_query      VARCHAR2(1000);
    --     v_column_name_lvl   VARCHAR2(50);
    --     v_column_name       VARCHAR2(50);
    -- BEGIN
    --     p_err := 0;

    --     --- step 0 : Apply sequence number
    --     update sp_raw_data set batch_id = (select NVL(max(batch_id),0) +1 from sp_raw_data where batch_id
    --                                                 is not null);
    --      commit;
    --     -- Step 1: Clean target table before inserting new analysis
    --     DELETE FROM SP_STOCK_TICKER_ANALYSIS;

    --     insert into sp_raw_data_archive select * from sp_raw_data;
    --     commit;

    --     -- Step 2: Insert distinct ticker data for the current date
    --     INSERT INTO SP_STOCK_TICKER_ANALYSIS (STOCK_NAME, ANALYSIS_TYPE, LAST_MODIFIED)
    --     SELECT DISTINCT NSE_NAME, 'TICKERTAPE', SYSDATE
    --     FROM SP_RAW_DATA ;


    --     COMMIT;

    --     -- Step 3: Iterate through each ticker attribute (Performance, Valuation, etc.)
    --     FOR att IN (
    --         SELECT TRIM(REGEXP_SUBSTR(
    --                     'Performance,Valuation,Growth,Profitability,Entry point,Red flags', 
    --                     '[^,]+', 1, LEVEL)) AS TT_att
    --         FROM dual
    --         CONNECT BY REGEXP_SUBSTR(
    --                     'Performance,Valuation,Growth,Profitability,Entry point,Red flags', 
    --                     '[^,]+', 1, LEVEL) IS NOT NULL
    --     )
    --     LOOP
    --         v_column_name_lvl := NULL;
    --         v_column_name     := NULL;

    --         -- Map attribute names to their corresponding table columns
    --         IF att.TT_att = 'Performance'   THEN v_column_name_lvl := 'PERFORMANCE_LEVEL';   v_column_name := 'PERFORMANCE';
    --         ELSIF att.TT_att = 'Valuation'  THEN v_column_name_lvl := 'VALUATION_LEVEL';     v_column_name := 'VALUATION';
    --         ELSIF att.TT_att = 'Growth'     THEN v_column_name_lvl := 'GROWTH_LEVEL';        v_column_name := 'GROWTH';
    --         ELSIF att.TT_att = 'Profitability' THEN v_column_name_lvl := 'PROFITABILITY_LEVEL'; v_column_name := 'PROFITABILITY';
    --         ELSIF att.TT_att = 'Entry point' THEN v_column_name_lvl := 'ENTRY_POINT_LEVEL';   v_column_name := 'ENTRY_POINT';
    --         ELSIF att.TT_att = 'Red flags'  THEN v_column_name_lvl := 'RED_FLAGS_LEVEL';     v_column_name := 'RED_FLAGS';
    --         END IF;

    --         -- Step 4: For each attribute, check possible level identifiers (1–5)
    --         FOR nu IN (
    --             SELECT TRIM(REGEXP_SUBSTR('1,2,3,4,5', '[^,]+', 1, LEVEL)) AS LVL
    --             FROM dual
    --             CONNECT BY REGEXP_SUBSTR('1,2,3,4,5', '[^,]+', 1, LEVEL) IS NOT NULL
    --         )
    --         LOOP
    --             cnt := nu.LVL;
    --             attribs := att.TT_att;

    --             -- Step 5: Extract corresponding performance details from raw data
    --             FOR i IN (
    --                 SELECT DISTINCT TRIM(REPLACE(TO_CHAR(SUBSTR(raw_data, INSTR(raw_data, '):') + 1)), ':', '')) AS perf,
    --                                 nse_name
    --                 FROM sp_raw_data
    --                 WHERE raw_data LIKE '%' || attribs || '%'
    --                   AND raw_data LIKE '%' || cnt || ')%'
    --             )
    --             LOOP
    --                 -- Step 6: Update LEVEL columns for known rating keywords
    --                 IF i.perf IS NOT NULL AND i.perf IN ('High','Low','Avg','Good') THEN
    --                     v_update_query := 
    --                         'UPDATE SP_STOCK_TICKER_ANALYSIS 
    --                          SET ' || v_column_name_lvl || ' = TRIM(REPLACE(:perf, '':'''''', '''')) 
    --                          WHERE STOCK_NAME = :nse_name';
    --                     EXECUTE IMMEDIATE v_update_query USING i.perf, i.nse_name;

    --                 -- Step 7: Update description column for additional data
    --                 ELSIF i.perf IS NOT NULL THEN
    --                     v_update_query :=
    --                         'UPDATE SP_STOCK_TICKER_ANALYSIS 
    --                          SET ' || v_column_name || ' = NVL(' || v_column_name || ', '''') || '','' || TRIM(REPLACE(:perf, '':'''''', '''')) 
    --                          WHERE STOCK_NAME = :nse_name';
    --                     EXECUTE IMMEDIATE v_update_query USING i.perf, i.nse_name;
    --                 END IF;
    --             END LOOP;
    --         END LOOP;
    --     END LOOP;

    --     COMMIT;

    -- EXCEPTION
    --     WHEN OTHERS THEN
    --         p_err := SQLCODE;
    --         p_err_desc := 'Exception in PRC_SP_TICKER_DATA_ANALYSE: ' || SQLERRM;
    -- END PRC_SP_TICKER_DATA_ANALYSE;



/* =================================================================================================
   Procedure: PRC_SP_TICKER_DATA_ANALYSE
   Purpose  : Analyzes raw ticker text and extracts key metrics like Performance, Valuation, etc.
              Populates SP_STOCK_TICKER_ANALYSIS with LEVEL (High/Low/Avg/Good) and description.
   ================================================================================================= */


PROCEDURE PRC_SP_TICKER_DATA_ANALYSE (
    p_err OUT NUMBER,
    p_err_desc OUT VARCHAR2
)
AS
    v_att_name          VARCHAR2(50);
    v_level_col         VARCHAR2(50);
    v_desc_col          VARCHAR2(50);
    v_level_value       VARCHAR2(100);
    v_desc_value        VARCHAR2(500);
    v_sql               VARCHAR2(4000);
BEGIN
    p_err := 0;

    -- Step 1: Backup and cleanup
    INSERT INTO sp_raw_data_archive SELECT * FROM sp_raw_data;
    DELETE FROM sp_stock_ticker_analysis;
    COMMIT;

    -- Step 2: Insert base records
    INSERT INTO sp_stock_ticker_analysis (stock_name, analysis_type, last_modified)
    SELECT DISTINCT nse_name, 'TICKERTAPE', SYSDATE
    FROM sp_raw_data;
    COMMIT;

    -- Step 3: Parse each record
    FOR r IN (SELECT nse_name, raw_data FROM sp_raw_data)
    LOOP
        FOR att IN (
            SELECT COLUMN_VALUE AS attr_name
            FROM TABLE(sys.odcivarchar2list(
                'Performance', 'Valuation', 'Growth', 'Profitability', 'Entry point', 'Red flags'))
        )
        LOOP
            v_att_name := att.attr_name;

            CASE v_att_name
                WHEN 'Performance'   THEN v_level_col := 'PERFORMANCE_LEVEL';   v_desc_col := 'PERFORMANCE';
                WHEN 'Valuation'     THEN v_level_col := 'VALUATION_LEVEL';     v_desc_col := 'VALUATION';
                WHEN 'Growth'        THEN v_level_col := 'GROWTH_LEVEL';        v_desc_col := 'GROWTH';
                WHEN 'Profitability' THEN v_level_col := 'PROFITABILITY_LEVEL'; v_desc_col := 'PROFITABILITY';
                WHEN 'Entry point'   THEN v_level_col := 'ENTRY_POINT_LEVEL';   v_desc_col := 'ENTRY_POINT';
                WHEN 'Red flags'     THEN v_level_col := 'RED_FLAGS_LEVEL';     v_desc_col := 'RED_FLAGS';
            END CASE;

            BEGIN
                SELECT 
                    TRIM(REGEXP_SUBSTR(r.raw_data, v_att_name || ':[[:space:]]*([^,]+)', 1, 1, NULL, 1)),
                    TRIM(REGEXP_SUBSTR(r.raw_data, v_att_name || ':[^,]+,[[:space:]]*(.*)', 1, 1, NULL, 1))
                INTO v_level_value, v_desc_value
                FROM dual;
            EXCEPTION
                WHEN NO_DATA_FOUND THEN
                    v_level_value := NULL;
                    v_desc_value := NULL;
            END;

            IF v_level_value IS NOT NULL THEN
                v_sql := 'UPDATE sp_stock_ticker_analysis
                          SET ' || v_level_col || ' = :lvl_value,
                              ' || v_desc_col  || ' = :desc_value
                          WHERE stock_name = :stock_name';

                EXECUTE IMMEDIATE v_sql
                    USING v_level_value, v_desc_value, r.nse_name;
            END IF;
        END LOOP;
    END LOOP;

    COMMIT;
    p_err := 0;
    p_err_desc := 'Success';

EXCEPTION
    WHEN OTHERS THEN
        p_err := SQLCODE;
        p_err_desc := 'Exception in PRC_SP_TICKER_DATA_ANALYSE: ' || SQLERRM;
END PRC_SP_TICKER_DATA_ANALYSE;


END PKG_STOCK_PULSE_ANALYSE;
/
