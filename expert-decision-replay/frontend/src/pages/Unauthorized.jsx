import { Link } from "react-router-dom";

const Unauthorized = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
        <div className="mb-4 text-6xl">🚫</div>

        <h1 className="mb-3 text-3xl font-bold text-red-600">
          403
        </h1>

        <h2 className="mb-3 text-xl font-semibold text-gray-800">
          Access Denied
        </h2>

        <p className="mb-6 text-gray-600">
          You are not authorized to access this page.
          Please contact your administrator if you need permission.
        </p>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link
            to="/dashboard"
            className="rounded-lg bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-700"
          >
            Go to Dashboard
          </Link>

          <button
            onClick={() => window.history.back()}
            className="rounded-lg border border-gray-300 px-5 py-3 font-medium text-gray-700 transition hover:bg-gray-100"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
};

export default Unauthorized;