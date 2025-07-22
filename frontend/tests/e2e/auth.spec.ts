import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

test.describe('Authentication Tests', () => {
  let loginPage: LoginPage;
  let registerPage: RegisterPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    registerPage = new RegisterPage(page);
  });

  test('User cannot login with non-existent credentials', async ({ page }) => {
    await loginPage.navigate();
    await loginPage.login('test@example.com', 'password123', false);
    
    // Verify unsuccessful login by checking we're still on login page
    expect(page.url()).toContain('/login');
    
    // Verify login button is still visible (meaning we haven't logged in)
    const loginButton = await page.getByRole('button', { name: /login/i });
    await expect(loginButton).toBeVisible();
  });

  test('User cannot login with invalid credentials', async ({ page }) => {
    await loginPage.navigate();
    await loginPage.login('invalid@email.com', 'wrongpassword', false);
    
    // Verify unsuccessful login by checking we're still on login page
    expect(page.url()).toContain('/login');
    
    // Verify login button is still visible (meaning we haven't logged in)
    const loginButton = await page.getByRole('button', { name: /login/i });
    await expect(loginButton).toBeVisible();
  });

  test('Cannot create account with duplicate email', async () => {
    await registerPage.navigate();
    await registerPage.register('Test User', 'test@gmail.com', 'testpassword');
    const errorMessage = await registerPage.getErrorMessage();
    expect(errorMessage).toContain('Failed to create account');
  });

  test('Can create new account with valid details', async () => {
    await registerPage.navigate();
    const randomEmail = `test${Math.random().toString(36).substring(7)}@gmail.com`;
    await registerPage.register('New Test User', randomEmail, 'testpassword123');
    await registerPage.waitForSuccessMessage();
    await expect(registerPage.getCurrentUrl()).resolves.toMatch(/.*\/login/);
  });
}); 