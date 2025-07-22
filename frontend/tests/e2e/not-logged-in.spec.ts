import { test, expect } from '@playwright/test';
import { HomePage } from './pages/HomePage';

test.describe('Not Logged In User Tests', () => {
  let homePage: HomePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.navigate();
  });

  test('Login and Register buttons are shown and redirect to respective pages', async () => {
    // Check login button
    const loginButton = await homePage.getLoginButton();
    await expect(loginButton).toBeVisible();
    await loginButton.click();
    await expect(homePage.getCurrentUrl()).resolves.toMatch(/.*\/\?tab=home/);

    // Navigate back to home
    await homePage.navigate();

    // Check register button
    const registerButton = await homePage.getRegisterButton();
    await expect(registerButton).toBeVisible();
    await registerButton.click();
    
    // Verify we're on the registration page by checking for the form
    const isRegistrationFormVisible = await homePage.isRegistrationFormVisible();
    expect(isRegistrationFormVisible).toBeTruthy();
  });

  test('Home, Quotes, and Authors tabs are shown to the user', async () => {
    const homeTab = await homePage.getHomeTab();
    const quotesTab = await homePage.getQuotesTab();
    const authorsTab = await homePage.getAuthorsTab();

    await expect(homeTab).toBeVisible();
    await expect(quotesTab).toBeVisible();
    await expect(authorsTab).toBeVisible();
  });

  test('Manage tab is not visible or accessible to the user when not logged in', async () => {
    const manageTab = await homePage.getManageTab();
    await expect(manageTab).not.toBeVisible();
  });
}); 