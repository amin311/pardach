describe('Navigation Tests', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should navigate to all main pages', () => {
    // تست ناوبری به صفحات اصلی
    cy.get('nav').within(() => {
      cy.get('a').each(($link) => {
        const href = $link.attr('href')
        if (href && !href.startsWith('#')) {
          cy.wrap($link).click()
          cy.url().should('include', href)
        }
      })
    })
  })

  it('should handle 404 errors correctly', () => {
    // تست صفحه 404
    cy.visit('/non-existent-page')
    cy.get('h1').should('contain', '404')
  })
}) 