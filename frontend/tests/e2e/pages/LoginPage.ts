import { Page, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  async navigate() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string, expectSuccess: boolean = true) {
    const emailInput = await this.getByLabel(/email/i);
    const passwordInput = await this.getByLabel(/password/i);
    const loginButton = await this.getByRole('button', { name: /login/i });
    
    await emailInput.fill(email);
    await passwordInput.fill(password);

    if (!expectSuccess) {
      // For failed login, just click and wait for the response
      await Promise.all([
        this.page.waitForResponse(
          response => response.url().includes('/auth/login') && response.status() === 401
        ),
        loginButton.click()
      ]);
      
      // Verify we're still on the login page
      await expect(this.page).toHaveURL(/.*\/login/);
    } else {
      // For successful login, wait for navigation
      await Promise.all([
        loginButton.click(),
        this.page.waitForURL('**/?tab=home')
      ]);
    }
  }

  async getErrorMessage() {
    return this.page.locator('div[role="status"]', {
      hasText: 'Invalid email or password'
    });
  }

  async isLoginFormVisible() {
    const form = await this.page.locator('form');
    return form.isVisible();
  }

  async isRegisterLinkVisible() {
    const registerLink = await this.getByRole('link', { name: /register/i });
    return registerLink.isVisible();
  }

  // New helper methods for auth tests
  async getManageTab() {
    return this.getByRole('tab', { name: /manage/i });
  }

  async getCurrentUrl() {
    return this.page.url();
  }
} 