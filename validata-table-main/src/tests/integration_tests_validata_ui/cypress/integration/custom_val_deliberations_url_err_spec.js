describe("Validator form use", function() {
  it("uses a schema url to validate a csv url", function() {
    const schema_url =
      "https://gitlab.com/opendatafrance/scdl/deliberations/raw/v2.1.2/schema.json"
    const csv_url =
      "https://gitlab.com/opendatafrance/scdl/deliberations/raw/v2.1.2/examples/Deliberations_coll_siret_ko.csv"

    cy.visit("")

    // Fill input textfield with schema URL and submit
    cy.get("form[data-cy=custom_schema_form]").within($form => {
      cy.get("input[name=schema_url]").type(schema_url)
      cy.root().submit()
    })

    // On validator form page,
    // click on 'URL' tab
    cy.get("a#url-tab.nav-link").click()

    // within form
    cy.get("div#url form").within($form => {
      cy.get("input[name=url]").type(csv_url)
      cy.root().submit()
    })

    // On report page
    cy.get("h2.card-title").contains("Fichier invalide")
    cy.get("a.btn").contains("Télécharger en PDF")
  })
})
