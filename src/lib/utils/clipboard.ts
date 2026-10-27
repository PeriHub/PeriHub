import { notify } from './notify';

export async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    notify.info('Copied to clipboard');
  } catch {
    notify.negative('Could not copy — select the value and copy it manually');
  }
}
