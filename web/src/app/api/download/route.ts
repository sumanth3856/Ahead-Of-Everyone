import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const fileId = searchParams.get('file_id');

  if (!fileId) {
    return new NextResponse('Missing file_id', { status: 400 });
  }

  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  if (!botToken) {
    return new NextResponse('Bot token not configured', { status: 500 });
  }

  try {
    // 1. Get file path from Telegram
    const getFileUrl = `https://api.telegram.org/bot${botToken}/getFile?file_id=${fileId}`;
    const getFileRes = await fetch(getFileUrl);
    const getFileData = await getFileRes.json();

    if (!getFileData.ok) {
      return new NextResponse('Failed to get file from Telegram: ' + getFileData.description, { status: 404 });
    }

    const filePath = getFileData.result.file_path;

    // 2. Stream the file
    const downloadUrl = `https://api.telegram.org/file/bot${botToken}/${filePath}`;
    const fileRes = await fetch(downloadUrl);
    
    if (!fileRes.ok) {
        return new NextResponse('Failed to download file', { status: 500 });
    }

    const headers = new Headers(fileRes.headers);
    headers.set('Content-Type', 'application/pdf');
    headers.set('Content-Disposition', `inline; filename="daily_digest.pdf"`);

    return new NextResponse(fileRes.body as any, {
      status: 200,
      headers
    });

  } catch (e) {
    console.error('Error downloading from Telegram:', e);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}
