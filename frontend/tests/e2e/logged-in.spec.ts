import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';
import { HomePage } from './pages/HomePage';

test.describe('Logged In User Tests', () => {
  let loginPage: LoginPage;
  let homePage: HomePage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    homePage = new HomePage(page);
    
    // Navigate and login
    await loginPage.navigate();
    await loginPage.login('test@gmail.com', 'testpassword');
  });

  test('User can see and click the logout button', async ({ page }) => {
    // Logout
    await homePage.logout();
    
    // Verify login form is visible
    const isLoginFormVisible = await loginPage.isLoginFormVisible();
    const isRegisterLinkVisible = await loginPage.isRegisterLinkVisible();
    
    expect(isLoginFormVisible).toBeTruthy();
    expect(isRegisterLinkVisible).toBeTruthy();
  });

  test('User can see and access the manage tab', async ({ page }) => {
    // Navigate to manage tab
    await homePage.navigateToManageTab();
    
    // Verify manage tab content
    const [isAddNewQuoteVisible, isQuoteTextInputVisible, isAuthorInputVisible] = 
      await homePage.isManageTabContentVisible();
    
    expect(isAddNewQuoteVisible).toBeTruthy();
    expect(isQuoteTextInputVisible).toBeTruthy();
    expect(isAuthorInputVisible).toBeTruthy();
  });

  test('User can like and unlike quotes', async ({ page }) => {
    // Navigate to quotes tab
    await homePage.navigateToQuotesTab();
    
    // Get the first quote's like button
    const likeButton = await homePage.getFirstQuoteLikeButton();
    await expect(likeButton).toBeVisible();
    
    // Get initial like count
    const initialLikeCount = await likeButton.textContent();
    
    // Click the like button and wait for both API calls to complete
    await Promise.all([
      // Wait for the like API call
      page.waitForResponse(response => response.url().includes('/quotes/') && response.status() === 200),
      // Wait for the quotes refetch
      page.waitForResponse(response => response.url().includes('/quotes') && !response.url().includes('/quotes/')),
      likeButton.click()
    ]);
    
    // Wait for the quotes to be refetched and UI to update
    await homePage.waitForNetworkIdle();
    
    // Verify the like count changed and heart is filled
    await expect(async () => {
      const newLikeCount = await likeButton.textContent();
      expect(newLikeCount).not.toBe(initialLikeCount);
      expect(await likeButton.textContent()).toContain('❤️');
    }).toPass({ timeout: 10000 });
    
    // Click again to unlike and wait for both API calls
    await Promise.all([
      // Wait for the unlike API call
      page.waitForResponse(response => response.url().includes('/quotes/') && response.status() === 200),
      // Wait for the quotes refetch
      page.waitForResponse(response => response.url().includes('/quotes') && !response.url().includes('/quotes/')),
      likeButton.click()
    ]);
    
    // Wait for the quotes to be refetched and UI to update
    await homePage.waitForNetworkIdle();
    
    // Verify the like count is back to initial and heart is empty
    await expect(async () => {
      const finalLikeCount = await likeButton.textContent();
      expect(finalLikeCount).toBe(initialLikeCount);
      expect(await likeButton.textContent()).toContain('🤍');
    }).toPass({ timeout: 10000 });
  });
}); 