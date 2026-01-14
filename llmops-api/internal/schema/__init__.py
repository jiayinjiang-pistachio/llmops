#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 08:06
@Author         : jiayinkong@163.com
@File           : __init__.py.py
@Description    : 请求和响应的结构体
"""
from .account_schema import GetCurrentUserResp, UpdatePasswordReq, UpdateNameReq, UpdateAvatarReq
from .api_tool_schema import ValidateOpenAPISchemaReq, CreateAPIToolReq, GetApiToolResp, GetApiToolProviderResp, \
    GetApiToolProvidersWithPageReq, GetApiToolProvidersWithPageResp, UpdateApiToolProviderReq
from .app_schema import CreateAppReq, GetAppResp, GetPublishHistoriesWithPageReq, GetPublishHistoriesWithPageResp, \
    FallbackHistoryToDraftReq, UpdateDebugConversationSummaryReq
from .dataset_schema import CreateDatasetReq, GetDatasetsWithPageReq, GetDatasetResp, UpdateDatasetReq, \
    GetDatasetsWithPageResp, HitReq
from .document_schema import CreateDocumentsReq, CreateDocumentsResp, UpdateDocumentEnabledReq
from .schema import ListField
from .segment_schema import GetSegmentsWithPageReq, GetSegmentsWithPageResp, UpdateSegmentEnabledReq, GetSegmentResp, \
    UpdateSegmentReq
from .upload_file_schema import UploadImageReq, UploadFileResp, UploadFileReq

__all__ = [
    "CreateAppReq",
    "GetAppResp",
    "GetPublishHistoriesWithPageReq",
    "GetPublishHistoriesWithPageResp",
    "FallbackHistoryToDraftReq",
    "UpdateDebugConversationSummaryReq",
    "ValidateOpenAPISchemaReq",
    "ListField",
    "CreateAPIToolReq",
    "GetApiToolResp",
    "GetApiToolProviderResp",
    "GetApiToolProvidersWithPageReq",
    "GetApiToolProvidersWithPageResp",
    "UpdateApiToolProviderReq",
    "UploadFileReq",
    "UploadFileResp",
    "UploadImageReq",
    "CreateDatasetReq",
    "GetDatasetsWithPageReq",
    "UpdateDatasetReq",
    "GetDatasetsWithPageResp",
    "GetDatasetResp",
    "CreateDocumentsReq",
    "CreateDocumentsResp",
    "UpdateDocumentEnabledReq",
    "HitReq",
    "UpdateSegmentReq",
    "GetCurrentUserResp",
    "UpdatePasswordReq",
    "UpdateNameReq",
    "UpdateAvatarReq",
]
