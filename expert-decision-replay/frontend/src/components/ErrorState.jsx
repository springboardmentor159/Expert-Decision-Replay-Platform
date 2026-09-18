const ErrorState = ({
  title = "Something went wrong",
  message = "Unable to load the data. Please try again.",
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-red-200 bg-red-50 px-6 py-12 text-center">
      <div className="mb-4 text-4xl">⚠️</div>

      <h3 className="text-lg font-semibold text-red-800">
        {title}
      </h3>

      <p className="mt-2 max-w-md text-sm text-red-600">
        {message}
      </p>

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
        >
          Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorState;