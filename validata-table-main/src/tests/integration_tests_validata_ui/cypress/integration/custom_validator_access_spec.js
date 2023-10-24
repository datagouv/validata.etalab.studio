describe("Validator form access", function() {
  it("loads a validation form from a schema url", function() {
    const schema_url =
      "https://gitlab.com/opendatafrance/scdl/subventions/raw/master/schema.json"

    cy.visit("")

    // Fill input textfield with schema URL and submit
    cy.get("form[data-cy=custom_schema_form]").within($form => {
      cy.get("input[name=schema_url]").type(schema_url)
      cy.root().submit()
    })

    // On validator form page

    // Check breadcrumbs
    cy.get("li.breadcrumb-item").contains("Autre schéma")

    // Check title in card
    cy.get("h2.card-title").contains("Subventions")

    // Check 'Valider le fichier' button
    cy.get("button").contains("Valider le fichier")
  })
})
