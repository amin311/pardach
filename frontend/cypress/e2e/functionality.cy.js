describe('Functionality Tests', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should handle form submissions correctly', () => {
    // تست ارسال فرم
    cy.get('form').within(() => {
      cy.get('input[type="text"]').type('Test User')
      cy.get('input[type="email"]').type('test@example.com')
      cy.get('button[type="submit"]').click()
    })
    
    // بررسی پیام موفقیت
    cy.get('.success-message').should('be.visible')
  })

  it('should validate form inputs', () => {
    // تست اعتبارسنجی فرم
    cy.get('form').within(() => {
      cy.get('input[type="email"]').type('invalid-email')
      cy.get('button[type="submit"]').click()
      cy.get('.error-message').should('be.visible')
    })
  })

  it('should handle button interactions', () => {
    // تست تعامل با دکمه‌ها
    cy.get('button').first().click()
    cy.get('.modal').should('be.visible')
    cy.get('.close-button').click()
    cy.get('.modal').should('not.exist')
  })
}) 