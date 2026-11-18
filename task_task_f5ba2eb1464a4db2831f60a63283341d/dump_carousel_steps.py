import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def inspect_transcript_carousel():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'rubric' not in pg.url][0]

    # Find the transcript pagination / messages
    res = await page.evaluate('''() => {
        // Find text saying "message" or "Transcript"
        const all = Array.from(document.querySelectorAll('*'));
        const transcriptEl = all.find(el => el.innerText && el.innerText.includes('Transcript') && el.innerText.includes('/ 44'));
        if (!transcriptEl) return { error: "Transcript el not found" };

        const parent = transcriptEl.closest('div');
        const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText ? b.innerText.trim() : '');
        return {
            transcriptText: transcriptEl.innerText,
            buttons: buttons.filter(t => t.includes('Next') || t.includes('Previous') || t.includes('Expand') || t.includes('Collapse') || t.includes('LOGS') || t.includes('DIFF'))
        };
    }''')
    print("Transcript carousel info:", res)

    # Let's see if we can loop through the 44 messages using Next button!
    messages = []
    for i in range(45):
        msg_text = await page.evaluate('''() => {
            // Find message container
            const cards = Array.from(document.querySelectorAll('div, section')).filter(el => {
                const t = el.innerText || '';
                return t.includes('Step ') || t.includes('Calling tool') || t.includes('[Thinking]') || t.includes('ROLE');
            });
            // Sort by shortest containing Step
            const stepCards = cards.filter(c => c.innerText.includes('Step '));
            if (stepCards.length > 0) {
                stepCards.sort((a, b) => a.innerText.length - b.innerText.length);
                return stepCards[stepCards.length - 1].innerText;
            }
            return '';
        }''')
        messages.append(f"=== MSG #{i+1} ===\n" + msg_text[:1500])

        # Click Next
        next_clicked = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const n = btns.find(b => (b.innerText || '').trim() === 'Next');
            if (n && !n.disabled) {
                n.click();
                return true;
            }
            return false;
        }''')
        if not next_clicked:
            print(f"Next button not available or disabled at step {i+1}")
            break
        await asyncio.sleep(0.3)

    print(f"Captured {len(messages)} messages via carousel!")
    with open('task_task_f5ba2eb1464a4db2831f60a63283341d/model_a/all_44_steps.txt', 'w', encoding='utf-8') as f:
        f.write("\n\n".join(messages))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_transcript_carousel())
