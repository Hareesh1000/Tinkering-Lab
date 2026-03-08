CREATE TABLE tx_watch_list (
  stock_id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  stock_name          VARCHAR(100) NOT NULL,
  stock_attrib_id     BIGINT,
  created_date        TIMESTAMPTZ DEFAULT now(),
  synch_date          TIMESTAMPTZ,
  
);