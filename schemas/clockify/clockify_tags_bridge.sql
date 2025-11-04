CREATE TABLE clockify_tags (
    row_id INT NOT NULL,
    tag NVARCHAR(255) NOT NULL,
    FOREIGN KEY (row_id) REFERENCES clockify_main(id)
);