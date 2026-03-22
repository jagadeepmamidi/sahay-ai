// API client for Sahay AI backend

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

async function fetchAPI<T>(
  endpoint: string,
  options: FetchOptions = {},
): Promise<T> {
  const { params, ...fetchOptions } = options;

  let url = `${API_BASE_URL}${endpoint}`;

  // Add query params
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers: {
      "Content-Type": "application/json",
      ...fetchOptions.headers,
    },
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "An error occurred" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Chat API
export async function sendMessage(
  message: string,
  sessionId?: string,
  language: string = "auto",
  userProfile?: Record<string, unknown>,
) {
  return fetchAPI("/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      session_id: sessionId,
      language,
      user_profile: userProfile,
    }),
  });
}

export async function getChatHistory(sessionId: string) {
  return fetchAPI(`/chat/history/${sessionId}`);
}

export async function submitFeedback(
  sessionId: string,
  messageId: string,
  rating: number,
  feedbackText?: string,
) {
  return fetchAPI("/chat/feedback", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      message_id: messageId,
      rating,
      feedback_text: feedbackText,
    }),
  });
}

export async function getSupportedLanguages() {
  return fetchAPI("/chat/languages");
}

// Schemes API
export async function getSchemes(
  page: number = 1,
  pageSize: number = 10,
  category?: string,
  schemeType?: string,
  search?: string,
) {
  return fetchAPI("/schemes", {
    params: {
      page,
      page_size: pageSize,
      category,
      scheme_type: schemeType,
      search,
    },
  });
}

export async function getSchemeDetails(schemeId: string) {
  return fetchAPI(`/schemes/${schemeId}`);
}

export async function checkEligibility(userProfile: Record<string, unknown>) {
  return fetchAPI("/schemes/eligibility", {
    method: "POST",
    body: JSON.stringify(userProfile),
  });
}

export async function quickSearch(query: string) {
  return fetchAPI("/schemes/search/quick", {
    params: { q: query },
  });
}

export async function getCategories() {
  return fetchAPI("/schemes/categories");
}

export async function getStates() {
  return fetchAPI("/schemes/states");
}

// Admin API
export async function uploadDocument(
  file: File,
  category: string,
  schemeName?: string,
) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("category", category);
  if (schemeName) {
    formData.append("scheme_name", schemeName);
  }

  // Special case for FormData as we need to omit Content-Type header to let browser set boundary
  const url = `${API_BASE_URL}/admin/upload`;
  const response = await fetch(url, {
    method: "POST",
    body: formData,
    headers: {
      // No Content-Type header here
    },
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail || "Upload failed");
  }

  return response.json();
}

export async function getJobStatus(jobId: string) {
  return fetchAPI(`/admin/jobs/${jobId}`);
}

export async function getAnalytics() {
  return fetchAPI("/admin/analytics");
}

// Health check
export async function healthCheck() {
  return fetchAPI("/health", {});
}

// Voice API
export async function transcribeAudio(file: File, language?: string) {
  const formData = new FormData();
  formData.append('file', file);
  if (language) {
    formData.append('language', language);
  }

  const url = `${API_BASE_URL}/voice/transcribe`;
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Transcription failed' }));
    throw new Error(error.detail || 'Transcription failed');
  }

  return response.json();
}

export async function translateText(
  text: string,
  sourceLanguage: string,
  targetLanguage: string
) {
  return fetchAPI("/voice/translate", {
    method: 'POST',
    body: JSON.stringify({
      text,
      source_language: sourceLanguage,
      target_language: targetLanguage,
    }),
  });
}

export async function synthesizeSpeech(text: string, language: string) {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('language', language);

  const url = `${API_BASE_URL}/voice/speak`;
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Speech synthesis failed');
  }

  return response.blob();
}

export async function getVoiceLanguages() {
  return fetchAPI("/voice/languages");
}
