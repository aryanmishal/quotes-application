import { Page, Locator } from '@playwright/test';

export class BasePage {
  constructor(protected page: Page) {}

  async waitForNetworkIdle() {
    await this.page.waitForLoadState('networkidle');
  }

  async waitForSelector(selector: string) {
    await this.page.waitForSelector(selector);
  }

  getByRole(role: 'button' | 'link' | 'tab' | 'textbox', options?: { name?: string | RegExp }): Locator {
    return this.page.getByRole(role, options);
  }

  async getByText(text: string | RegExp) {
    return this.page.getByText(text);
  }

  async getByLabel(label: string | RegExp) {
    return this.page.getByLabel(label);
  }
} 