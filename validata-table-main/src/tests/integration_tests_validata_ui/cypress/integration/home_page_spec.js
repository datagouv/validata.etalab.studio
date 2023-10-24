describe("The Home Page", function() {
  it("successfully loads", function() {
    // Loads home-page
    cy.visit("");

    // Checks that schema name select exists
    cy.get("select[name=schema_name]").should($select => {
      // and contains <option>
      expect($select).to.have.descendants("option");
    });

    // Checks that schema url input exists
    cy.get("input[name=schema_url]");
  });
});
