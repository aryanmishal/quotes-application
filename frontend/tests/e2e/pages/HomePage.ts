import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class HomePage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  async navigate() {
    await this.page.goto('http://localhost:3000');
  }

  async logout() {
    const logoutButton = await this.getByRole('button', { name: /logout/i });
    await logoutButton.click();
    await this.page.waitForURL('**/login');
    await this.waitForNetworkIdle();
  }

  async navigateToManageTab() {
    const manageTab = await this.getByRole('tab', { name: /manage/i });
    await manageTab.click();
    await this.page.waitForSelector('[data-testid="manage-tab-content"]', { state: 'visible' });
  }

  async navigateToQuotesTab() {
    const quotesTab = await this.page.locator('button[role="tab"]:has-text("Quotes"):not(:has-text("My"))').first();
    await quotesTab.click();
    await this.page.waitForSelector('[data-testid="quotes-list"]', { state: 'visible' });
  }

  async getFirstQuoteLikeButton() {
    await this.page.waitForSelector('[data-testid="quote-like-button"]', { state: 'visible' });
    return this.page.locator('[data-testid="quote-like-button"]').first();
  }

  async waitForQuotesToLoad() {
    await this.waitForSelector('[data-slot="card"]');
  }

  async waitForManageTabContent() {
    await this.waitForSelector('[data-state="active"]');
  }

  async isManageTabContentVisible() {
    await this.page.waitForSelector('[data-testid="manage-tab-content"]', { state: 'visible' });
    const addNewQuoteButton = await this.page.locator('[data-testid="add-quote-button"]');
    const quoteTextInput = await this.page.locator('[data-testid="quote-text-input"]');
    const authorInput = await this.page.locator('[data-testid="author-input"]');
    
    return Promise.all([
      addNewQuoteButton.isVisible(),
      quoteTextInput.isVisible(),
      authorInput.isVisible()
    ]);
  }

  // New helper methods for not-logged-in tests
  async getLoginButton() {
    return this.getByText(/login/i);
  }

  async getRegisterButton() {
    return this.getByText(/register/i);
  }

  async getHomeTab() {
    return this.getByRole('tab', { name: /home/i });
  }

  async getQuotesTab() {
    return this.getByRole('tab', { name: /quotes/i });
  }

  async getAuthorsTab() {
    return this.getByRole('tab', { name: /authors/i });
  }

  async getManageTab() {
    return this.getByRole('tab', { name: /manage/i });
  }

  async getCurrentUrl() {
    return this.page.url();
  }

  async isRegistrationFormVisible() {
    await this.waitForSelector('form');
    const form = await this.page.locator('form');
    return form.isVisible();
  }

  async waitForQuoteUpdate() {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(1000);
  }
} 