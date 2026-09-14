const PageHeader = ({
  title,
  subtitle,
  action,
}) => {
  return (
    <div className="page-header">

      <div>
        <h1>{title}</h1>

        {subtitle && (
          <p>{subtitle}</p>
        )}
      </div>

      {action && (
        <div className="page-header-action">
          {action}
        </div>
      )}

    </div>
  );
};

export default PageHeader;