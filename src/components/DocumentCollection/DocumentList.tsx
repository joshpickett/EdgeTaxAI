interface DocumentListProps {
  documents: Array<any>;
  requiredDocuments: Array<any>;
  showMetadata?: boolean;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  requiredDocuments,
  showMetadata = false
}) => {
  return (
    <div>
      {documents.map(doc => (
        <div key={doc.id}>
          <span className="document-name">{doc.name}</span>
          <span className="document-status">
            {doc.status}
          </span>
          {showMetadata && doc.metadata && (
            <div className="document-metadata">
              <h4>Extracted Information:</h4>
              <ul>
                {Object.entries(doc.metadata).map(([key, value]) => (
                  <li key={key}>{key}: {value}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
