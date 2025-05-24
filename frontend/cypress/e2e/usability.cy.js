describe('Usability Tests', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should have responsive layout', () => {
    // تست ریسپانسیو بودن در سایزهای مختلف
    cy.viewport(320, 480) // موبایل
    cy.get('.responsive-container').should('be.visible')
    
    cy.viewport(768, 1024) // تبلت
    cy.get('.responsive-container').should('be.visible')
    
    cy.viewport(1920, 1080) // دسکتاپ
    cy.get('.responsive-container').should('be.visible')
  })

  it('should have accessible elements', () => {
    // تست دسترسی‌پذیری
    cy.get('button').should('have.attr', 'aria-label')
    cy.get('img').should('have.attr', 'alt')
    cy.get('input').should('have.attr', 'aria-label')
  })

  it('should have proper loading states', () => {
    // تست وضعیت‌های بارگذاری
    cy.get('button.loading').click()
    cy.get('.loading-spinner').should('be.visible')
    cy.get('.loading-spinner').should('not.exist')
  })
}) 