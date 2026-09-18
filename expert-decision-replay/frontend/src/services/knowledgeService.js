import api from "./api";

const searchKnowledge = async ({
  search = "",
  category = "",
  status = "",
} = {}) => {
  const params = {};

  if (search.trim()) {
    params.q = search.trim();
  }

  if (category.trim()) {
    params.category = category.trim();
  }

  if (status) {
    params.status = status;
  }

  let response;

  // If search text is entered, use the dedicated search endpoint.
  if (search.trim()) {
    response = await api.get("/decisions/search", {
      params,
    });

    return response.data?.results || [];
  }

  // If search text is empty, use the normal decisions endpoint.
  // This endpoint supports category and status filters.
  response = await api.get("/decisions", {
    params,
  });

  return Array.isArray(response.data)
    ? response.data
    : [];
};

const getKnowledgeRepository = async () => {
  const response = await api.get("/decisions");
  return response.data;
};

const knowledgeService = {
  searchKnowledge,
  getKnowledgeRepository,
};

export default knowledgeService;