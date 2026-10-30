// Funciones para pegar con javascript_tool en una pestaña de scopus.com con sesión iniciada.
// Evitan el diálogo de exportación (frágil en el Browser pane de Claude).
//
// 1) Conteo y registros con resumen:
//      await scopusBuscar('TITLE-ABS-KEY(...) AND PUBYEAR > 2021 ...', 200)
//    -> {total, items:[{Authors, Title, Year, Source title, Volume, Issue, Page start, Page end,
//                       Cited by, DOI, Abstract, Open Access, EID, ...}]}
// 2) Exportación oficial de Scopus (CSV o RIS), igual a la del botón Export:
//      await scopusExportar('EID(2-s2.0-...) OR EID(2-s2.0-...)', 4, 'RIS')   // o 'CSV'
//    -> texto del archivo. Para guardarlo: devolver JSON.stringify({txt, pad:'x'.repeat(300000)})
//       y decodificar con guardar_desde_navegador.py --json-key txt

async function scopusBuscar(query, itemcount = 200) {
  const r = await fetch('/api/documents/search', {
    method: 'POST', credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ documentClassificationEnum: 'primary', query, sort: 'plf-f', itemcount, offset: 0, showAbstract: true })
  });
  const j = await r.json();
  const items = (j.items || []).map(it => ({
    'Authors': (it.authors || []).map(a => a.preferredName?.full).join('; '),
    'Title': (it.titles || [it.title])[0], 'Year': it.pubYear, 'Source title': it.source?.title,
    'Volume': it.sourceRelationship?.volume || '', 'Issue': it.sourceRelationship?.issue || '',
    'Art. No.': it.sourceRelationship?.articleNumber || '',
    'Page start': it.sourceRelationship?.pages?.pageFirst || '', 'Page end': it.sourceRelationship?.pages?.pageLast || '',
    'Cited by': it.citations?.count ?? '', 'DOI': it.doi || '', 'Abstract': (it.abstractText || []).join(' '),
    'Publisher': it.source?.publisher || '', 'Document Type': it.documentType, 'Publication Stage': it.publicationStage,
    'Open Access': it.freetoread ? 'Free to read' : '', 'Subject': (it.subjectAreas || []).map(s => s.displayName).join('; '),
    'EID': it.eid
  }));
  return { total: j.metadata?.totalCount, items };
}

async function scopusExportar(query, itemCount, fileType = 'RIS') {
  const campos = ['authors', 'titles', 'year', 'eid', 'sourceTitle', 'volumeIssuePages', 'citedBy', 'source', 'documentType',
    'publicationStage', 'doi', 'openAccess', 'affiliations', 'serialIdentifiers', 'pubMedId', 'publisher', 'editors',
    'originalLanguage', 'correspondenceAddress', 'abbreviatedSourceTitle', 'abstract', 'authorKeywords', 'indexedKeywords',
    'fundingDetails', 'fundingTexts', 'tradenamesAndManufacturers', 'accessionNumbersAndChemicals', 'conferenceInformation', 'references'];
  const base = '/gateway/export-service-reactive/export/bulk-job';
  const ini = await fetch(`${base}/initiate`, {
    method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      searchRequest: { query, documentClassification: 'PRIMARY',
        sortBy: [{ fieldName: 'datesort', order: 'desc' }, { fieldName: 'relevance', order: 'desc' }],
        resultSet: { offset: 0, itemCount } },
      fileType, exportType: 'PUBLICATION', fieldGroupIdentifiers: campos, locale: 'en-US', userQuery: query
    })
  });
  const job = await ini.json();
  const id = job.bulkExportId || job.id || job.jobId || JSON.stringify(job).match(/[0-9a-f]{8}-[0-9a-f-]{27}/)[0];
  for (let k = 0; k < 20; k++) {
    await new Promise(r => setTimeout(r, 2000));
    const g = await fetch(`${base}/${id}/generate-url`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' } });
    if (g.ok) {
      const j = await g.json();
      if (j.presignedUrl) return await (await fetch(j.presignedUrl)).text();
    }
  }
  throw new Error('La exportación no terminó a tiempo: ' + id);
}
