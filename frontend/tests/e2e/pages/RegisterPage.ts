import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class RegisterPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  async navigate() {
    await this.page.goto('http://localhost:3000');
    const registerButton = await this.getByText(/register/i);
    await registerButton.click();
    await this.waitForSelector('form');
  }

  async register(name: string, email: string, password: string) {
    const nameInput = await this.getByLabel(/name/i);
    const emailInput = await this.getByLabel(/email/i);
    const passwordInput = await this.getByLabel(/password/i);
    const registerButton = await this.getByRole('button', { name: /create account/i });

    await nameInput.fill(name);
    await emailInput.fill(email);
    await passwordInput.fill(password);
    await registerButton.click();
    
    // Wait for either success or error message
    await Promise.race([
      this.waitForSelector('text=account created successfully'),
      this.waitForSelector('text=failed to create account')
    ]);
  }

  async isRegistrationFormVisible() {
    const form = await this.page.locator('form');
    return form.isVisible();
  }

  async getErrorMessage() {
    await this.waitForSelector('text=failed to create account');
    const errorMessage = await this.page.locator('text=failed to create account');
    return errorMessage.textContent();
  }

  async waitForSuccessMessage() {
    await this.waitForSelector('text=account created successfully');
  }

  async getCurrentUrl() {
    return this.page.url();
  }
} 