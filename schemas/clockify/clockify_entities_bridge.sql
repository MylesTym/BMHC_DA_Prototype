CREATE TABLE clockify_entities (
    row_id INT NOT NULL,
    org_id INT NOT NULL,
    FOREIGN KEY (row_id) REFERENCES clockify_main(id),
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);