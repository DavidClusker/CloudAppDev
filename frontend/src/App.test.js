import { fireEvent, render, screen } from '@testing-library/react';
import axios from 'axios';
import App from './App';

jest.mock('axios');

test('shows a validation message and does not submit when the name is empty', async () => {
  axios.get.mockResolvedValue({ data: [] });

  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Create' }));

  expect(await screen.findByRole('alert')).toHaveTextContent(
    'Item cannot be empty,please provide a valid item name'
  );
  expect(axios.post).not.toHaveBeenCalled();
});
