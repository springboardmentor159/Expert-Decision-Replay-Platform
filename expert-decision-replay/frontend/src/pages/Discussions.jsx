import React, { useEffect, useState } from "react";
import discussionService from "../services/discussionService";

const Discussions = () => {
  const [discussions, setDiscussions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDiscussion, setSelectedDiscussion] = useState(null);
  const [newComment, setNewComment] = useState("");
  const [commentLoading, setCommentLoading] = useState(false);

  const loadDiscussions = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await discussionService.getDiscussions();

      setDiscussions(response.data || response || []);
    } catch (err) {
      console.error("Error loading discussions:", err);
      setError("Unable to load discussions.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDiscussions();
  }, []);

  const handleViewDiscussion = async (discussion) => {
    try {
      const response = await discussionService.getDiscussionById(
        discussion.id
      );

      setSelectedDiscussion(response.data || response);
    } catch (err) {
      console.error("Error loading discussion details:", err);
      setSelectedDiscussion(discussion);
    }
  };

  const handleAddComment = async (event) => {
    event.preventDefault();

    if (!newComment.trim() || !selectedDiscussion) {
      return;
    }

    try {
      setCommentLoading(true);

      await discussionService.addComment(selectedDiscussion.id, {
        content: newComment,
      });

      setNewComment("");
      alert("Comment added successfully.");

      handleViewDiscussion(selectedDiscussion);
    } catch (err) {
      console.error("Error adding comment:", err);
      alert("Unable to add comment.");
    } finally {
      setCommentLoading(false);
    }
  };

  const getStatusStyle = (status) => {
    switch (status?.toLowerCase()) {
      case "open":
        return "bg-green-100 text-green-700";

      case "closed":
        return "bg-gray-100 text-gray-700";

      case "resolved":
        return "bg-blue-100 text-blue-700";

      default:
        return "bg-yellow-100 text-yellow-700";
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Discussions</h1>
        <p className="text-gray-600">Loading discussions...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            Discussions
          </h1>

          <p className="text-gray-600 mt-1">
            View decision discussions and add comments.
          </p>
        </div>

        <button
          onClick={loadDiscussions}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="p-4 border-b bg-gray-50">
            <h2 className="font-semibold text-gray-800">
              Discussion Threads
            </h2>
          </div>

          {discussions.length === 0 ? (
            <div className="p-6 text-center text-gray-600">
              No discussions found.
            </div>
          ) : (
            <div className="divide-y">
              {discussions.map((discussion) => (
                <div
                  key={discussion.id}
                  className="p-4 hover:bg-gray-50"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-semibold text-gray-800">
                        {discussion.title ||
                          discussion.subject ||
                          `Discussion #${discussion.id}`}
                      </h3>

                      <p className="text-sm text-gray-600 mt-1">
                        {discussion.description ||
                          discussion.content ||
                          "No description available."}
                      </p>
                    </div>

                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap ${getStatusStyle(
                        discussion.status
                      )}`}
                    >
                      {discussion.status || "Open"}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-3 text-xs text-gray-500 mt-3">
                    <span>
                      ID: {discussion.id}
                    </span>

                    <span>
                      Decision: {discussion.decision_id || "-"}
                    </span>

                    <span>
                      User: {discussion.created_by || discussion.user_id || "-"}
                    </span>
                  </div>

                  <button
                    onClick={() => handleViewDiscussion(discussion)}
                    className="mt-3 text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Discussion
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow">
          <div className="p-4 border-b bg-gray-50">
            <h2 className="font-semibold text-gray-800">
              Discussion Details
            </h2>
          </div>

          {!selectedDiscussion ? (
            <div className="p-6 text-center text-gray-600">
              Select a discussion to view details.
            </div>
          ) : (
            <div className="p-5">
              <h3 className="text-xl font-semibold text-gray-800">
                {selectedDiscussion.title ||
                  selectedDiscussion.subject ||
                  `Discussion #${selectedDiscussion.id}`}
              </h3>

              <p className="text-gray-600 mt-2">
                {selectedDiscussion.description ||
                  selectedDiscussion.content ||
                  "No description available."}
              </p>

              <div className="mt-4 space-y-2 text-sm">
                <p>
                  <strong>Discussion ID:</strong>{" "}
                  {selectedDiscussion.id}
                </p>

                <p>
                  <strong>Decision ID:</strong>{" "}
                  {selectedDiscussion.decision_id || "-"}
                </p>

                <p>
                  <strong>Status:</strong>{" "}
                  {selectedDiscussion.status || "Open"}
                </p>
              </div>

              <div className="mt-6">
                <h4 className="font-semibold text-gray-800 mb-3">
                  Comments
                </h4>

                {selectedDiscussion.comments?.length > 0 ? (
                  <div className="space-y-3">
                    {selectedDiscussion.comments.map((comment) => (
                      <div
                        key={comment.id}
                        className="bg-gray-50 rounded-lg p-3"
                      >
                        <p className="text-gray-800">
                          {comment.content || comment.comment}
                        </p>

                        <p className="text-xs text-gray-500 mt-2">
                          User: {comment.user_id || comment.created_by || "-"}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">
                    No comments available.
                  </p>
                )}
              </div>

              <form
                onSubmit={handleAddComment}
                className="mt-5"
              >
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Add Comment
                </label>

                <textarea
                  value={newComment}
                  onChange={(event) =>
                    setNewComment(event.target.value)
                  }
                  placeholder="Write your comment..."
                  rows="3"
                  className="w-full border rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <button
                  type="submit"
                  disabled={commentLoading || !newComment.trim()}
                  className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {commentLoading ? "Adding..." : "Add Comment"}
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Discussions;