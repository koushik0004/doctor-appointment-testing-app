from app.knowledge import (
    KnowledgeDocument,
    KnowledgeDocumentAudience,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeDocumentStatus,
    KnowledgePromptHints,
)
from app.services.prompt_builder import (
    PromptBuildRequest,
    PromptAssemblySection,
    PromptAssemblySectionKind,
    PromptBuilderService,
    PromptContextAssemblyPipeline,
    PromptContext,
    PromptContextConstraints,
    PromptContextConversationCollector,
    PromptContextConversationContext,
    PromptContextKnowledgeCollector,
    PromptContextKnowledgeContext,
    PromptContextKnowledgeDocument,
    PromptContextMetadata,
    PromptContextRenderingOptions,
    PromptRenderer,
    PromptContextSystemInstructionBuilder,
    PromptContextSystemInstructions,
    PromptContextUserContext,
    PromptContextValidationResult,
    PromptContextWorkflowCollector,
    PromptContextWorkflowContext,
)


def _build_document(
    *,
    document_id: str,
    title: str = "Test Document",
    summary: str = "Test summary.",
    content: str | dict = "Test content.",
    include_when_intents: list[str] | None = None,
    exclude_when_intents: list[str] | None = None,
    safe_to_quote: bool = True,
    requires_domain_validation: bool = False,
    max_context_chars: int | None = None,
    metadata: dict | None = None,
) -> KnowledgeDocument:
    return KnowledgeDocument(
        id=document_id,
        title=title,
        source_type=KnowledgeDocumentSourceType.MARKDOWN,
        source_path=f"faq/{document_id}.md",
        domain=KnowledgeDocumentDomain.FAQ,
        audience=KnowledgeDocumentAudience.PATIENT,
        status=KnowledgeDocumentStatus.ACTIVE,
        version="1.0",
        summary=summary,
        content=content,
        prompt_hints=KnowledgePromptHints(
            include_when_intents=include_when_intents or [],
            exclude_when_intents=exclude_when_intents or [],
            safe_to_quote=safe_to_quote,
            requires_domain_validation=requires_domain_validation,
            max_context_chars=max_context_chars,
        ),
        metadata=metadata or {},
    )


def test_prompt_builder_builds_deterministic_prompt_with_context_blocks():
    service = PromptBuilderService()
    document = _build_document(
        document_id="faq.booking",
        title="Booking Help",
        content={"steps": ["choose doctor", "pick time"]},
    )

    result = service.build(
        PromptBuildRequest(
            user_message="Help me book an appointment",
            conversation_state={"workflow": "BOOK_APPOINTMENT", "missing": ["date"]},
            documents=[document],
            system_instructions=["Use only provided context.", "Do not invent appointment data."],
        )
    )

    assert result.truncated is False
    assert result.included_document_ids == ["faq.booking"]
    assert result.excluded_document_ids == []
    assert result.blocks[0].label == "User Message"
    assert result.blocks[1].label == "Conversation State"
    assert result.blocks[2].label == "Workflow State"
    assert result.blocks[3].metadata["document_id"] == "faq.booking"
    assert "[System Instructions]" in result.prompt
    assert '"missing":["date"]' in result.prompt
    assert '"active_intent":"BOOK_APPOINTMENT"' in result.prompt
    assert '"steps":["choose doctor","pick time"]' in result.prompt


def test_prompt_builder_creates_canonical_prompt_context_with_optional_sections():
    service = PromptBuilderService()
    document = _build_document(
        document_id="faq.booking",
        title="Booking Help",
        include_when_intents=["BOOK_APPOINTMENT"],
        requires_domain_validation=True,
    )

    context = service.build_context(
        PromptBuildRequest(
            user_message="Help me book",
            conversation_state={"draft": {"doctor_id": 1}},
            documents=[document],
            active_intent="BOOK_APPOINTMENT",
            system_instructions=["Use only provided context."],
            max_prompt_chars=2500,
        )
    )

    assert context.metadata.active_intent == "BOOK_APPOINTMENT"
    assert context.metadata.included_document_ids == ["faq.booking"]
    assert context.metadata.excluded_document_ids == []
    assert context.metadata.requires_domain_validation is True
    assert context.user_context.message == "Help me book"
    assert context.conversation_context is not None
    assert context.conversation_context.state == {"draft": {"doctor_id": 1}}
    assert context.workflow_context is not None
    assert context.workflow_context.active_intent == "BOOK_APPOINTMENT"
    assert context.knowledge_context is not None
    assert context.knowledge_context.documents[0].document_id == "faq.booking"
    assert context.system_instructions.instructions == ["Use only provided context."]
    assert context.constraints.max_prompt_chars == 2500


def test_prompt_builder_context_uses_deterministic_defaults_for_optional_sections():
    service = PromptBuilderService()

    context = service.build_context(
        PromptBuildRequest(
            user_message="Hello there",
        )
    )

    assert context.metadata.included_document_ids == []
    assert context.metadata.excluded_document_ids == []
    assert context.metadata.requires_domain_validation is False
    assert context.conversation_context is None
    assert context.workflow_context is None
    assert context.knowledge_context is None
    assert context.system_instructions.instructions == []
    assert context.constraints == PromptContextConstraints()
    assert context.rendering_options == PromptContextRenderingOptions()


def test_system_instruction_builder_returns_empty_instructions_by_default():
    builder = PromptContextSystemInstructionBuilder()

    instructions = builder.build(caller_instructions=[])

    assert instructions == PromptContextSystemInstructions(instructions=[])


def test_system_instruction_builder_returns_application_rules_when_present():
    builder = PromptContextSystemInstructionBuilder(
        application_rules=[
            "Use only provided context.",
            "Keep answers provider-agnostic.",
        ]
    )

    instructions = builder.build(caller_instructions=[])

    assert instructions == PromptContextSystemInstructions(
        instructions=[
            "Use only provided context.",
            "Keep answers provider-agnostic.",
        ]
    )


def test_system_instruction_builder_preserves_caller_instructions():
    builder = PromptContextSystemInstructionBuilder()

    instructions = builder.build(
        caller_instructions=[
            "Do not invent appointment data.",
            "Prefer deterministic summaries.",
        ]
    )

    assert instructions == PromptContextSystemInstructions(
        instructions=[
            "Do not invent appointment data.",
            "Prefer deterministic summaries.",
        ]
    )


def test_system_instruction_builder_merges_rules_and_deduplicates_deterministically():
    builder = PromptContextSystemInstructionBuilder(
        application_rules=[
            "Use only provided context.",
            "Do not invent appointment data.",
            "Use only provided context.",
        ]
    )
    caller_instructions = [
        "Do not invent appointment data.",
        "Prefer deterministic summaries.",
        "  Prefer deterministic summaries.  ",
        "",
    ]

    instructions = builder.build(caller_instructions=caller_instructions)

    assert instructions == PromptContextSystemInstructions(
        instructions=[
            "Use only provided context.",
            "Do not invent appointment data.",
            "Prefer deterministic summaries.",
        ]
    )
    assert caller_instructions == [
        "Do not invent appointment data.",
        "Prefer deterministic summaries.",
        "  Prefer deterministic summaries.  ",
        "",
    ]


def test_prompt_assembly_pipeline_orders_sections_deterministically():
    pipeline = PromptContextAssemblyPipeline()
    context = PromptContext(
        metadata=PromptContextMetadata(included_document_ids=["faq.booking"]),
        user_context=PromptContextUserContext(message="Help me book"),
        conversation_context=PromptContextConversationContext(
            state={"conversation_id": "conv-1"},
            current_user_message="Help me book",
        ),
        workflow_context=PromptContextWorkflowContext(
            active_intent="BOOK_APPOINTMENT",
            workflow_status="INPUT_REQUIRED",
            collected_fields={"doctor_name": "Dr. Smith"},
            missing_fields=["appointment_date"],
        ),
        knowledge_context=PromptContextKnowledgeContext(
            documents=[
                PromptContextKnowledgeDocument(
                    document_id="faq.booking",
                    title="Booking Help",
                    source_path="faq/booking.md",
                    domain="faq",
                    audience="patient",
                    summary="Booking summary.",
                    content="Booking content.",
                    safe_to_quote=True,
                )
            ]
        ),
        system_instructions=PromptContextSystemInstructions(
            instructions=["Use only provided context."]
        ),
    )

    sections = pipeline.assemble(context)

    assert [section.kind for section in sections] == [
        PromptAssemblySectionKind.SYSTEM_INSTRUCTIONS,
        PromptAssemblySectionKind.USER_MESSAGE,
        PromptAssemblySectionKind.CONVERSATION_STATE,
        PromptAssemblySectionKind.WORKFLOW_STATE,
        PromptAssemblySectionKind.KNOWLEDGE_DOCUMENT,
    ]
    assert sections[0].label == "System Instructions"
    assert sections[3].label == "Workflow State"
    assert '"active_intent":"BOOK_APPOINTMENT"' in sections[3].content
    assert '"missing_fields":["appointment_date"]' in sections[3].content
    assert sections[4].metadata == {
        "document_id": "faq.booking",
        "source_path": "faq/booking.md",
        "domain": "faq",
        "audience": "patient",
    }


def test_prompt_assembly_pipeline_omits_empty_sections_automatically():
    pipeline = PromptContextAssemblyPipeline()
    context = PromptContext(
        metadata=PromptContextMetadata(),
        user_context=PromptContextUserContext(message="Hello there"),
        conversation_context=PromptContextConversationContext(),
        system_instructions=PromptContextSystemInstructions(instructions=[]),
    )

    sections = pipeline.assemble(context)

    assert [section.kind for section in sections] == [PromptAssemblySectionKind.USER_MESSAGE]


def test_prompt_assembly_pipeline_is_deterministic_and_read_only():
    pipeline = PromptContextAssemblyPipeline()
    context = PromptContext(
        metadata=PromptContextMetadata(included_document_ids=["faq.policy"]),
        user_context=PromptContextUserContext(message="What should I bring?"),
        knowledge_context=PromptContextKnowledgeContext(
            documents=[
                PromptContextKnowledgeDocument(
                    document_id="faq.policy",
                    title="Booking Policy",
                    source_path="faq/policy.md",
                    domain="faq",
                    audience="patient",
                    summary="Bring ID.",
                    content={"policy": "Bring ID"},
                    safe_to_quote=True,
                    metadata={"revision": 3},
                )
            ]
        ),
    )
    original_context = context.model_copy(deep=True)

    first_sections = pipeline.assemble(context)
    second_sections = pipeline.assemble(context)

    assert first_sections == second_sections
    assert context == original_context
    assert first_sections[1].metadata == {
        "document_id": "faq.policy",
        "source_path": "faq/policy.md",
        "domain": "faq",
        "audience": "patient",
    }


def test_prompt_renderer_is_deterministic_with_headers_enabled():
    renderer = PromptRenderer()
    sections = [
        PromptAssemblySection(
            kind=PromptAssemblySectionKind.USER_MESSAGE,
            label="User Message",
            content="Need help booking",
        ),
        PromptAssemblySection(
            kind=PromptAssemblySectionKind.CONVERSATION_STATE,
            label="Conversation State",
            content='{"history":[]}',
        ),
        PromptAssemblySection(
            kind=PromptAssemblySectionKind.WORKFLOW_STATE,
            label="Workflow State",
            content='{"active_intent":"BOOK_APPOINTMENT"}',
        ),
    ]
    options = PromptContextRenderingOptions(include_section_headers=True)

    first_result = renderer.render(
        sections=sections,
        rendering_options=options,
        max_prompt_chars=400,
    )
    second_result = renderer.render(
        sections=sections,
        rendering_options=options,
        max_prompt_chars=400,
    )

    assert first_result == second_result
    assert first_result.truncated is False
    assert first_result.prompt == (
        "[User Message]\nNeed help booking\n\n"
        "[Conversation State]\n{\"history\":[]}\n\n"
        "[Workflow State]\n{\"active_intent\":\"BOOK_APPOINTMENT\"}"
    )


def test_prompt_renderer_supports_headers_disabled():
    renderer = PromptRenderer()
    sections = [
        PromptAssemblySection(
            kind=PromptAssemblySectionKind.USER_MESSAGE,
            label="User Message",
            content="Need help booking",
        ),
    ]

    result = renderer.render(
        sections=sections,
        rendering_options=PromptContextRenderingOptions(include_section_headers=False),
        max_prompt_chars=400,
    )

    assert result.prompt == "Need help booking"
    assert result.truncated is False


def test_prompt_renderer_returns_empty_prompt_for_empty_sections():
    renderer = PromptRenderer()

    result = renderer.render(
        sections=[],
        rendering_options=PromptContextRenderingOptions(),
        max_prompt_chars=400,
    )

    assert result.prompt == ""
    assert result.truncated is False


def test_prompt_renderer_applies_total_prompt_truncation_and_marker():
    renderer = PromptRenderer()
    sections = [
        PromptAssemblySection(
            kind=PromptAssemblySectionKind.USER_MESSAGE,
            label="User Message",
            content="A" * 80,
        ),
    ]

    result = renderer.render(
        sections=sections,
        rendering_options=PromptContextRenderingOptions(truncation_marker="[CUT]"),
        max_prompt_chars=40,
    )

    assert result.truncated is True
    assert result.prompt.endswith("\n\n[CUT]")
    assert len(result.prompt) <= 40


def test_prompt_renderer_is_read_only():
    renderer = PromptRenderer()
    sections = [
        PromptAssemblySection(
            kind=PromptAssemblySectionKind.KNOWLEDGE_DOCUMENT,
            label="Knowledge Document: Booking Help",
            content="Summary: Bring ID",
            metadata={"document_id": "faq.booking"},
        ),
    ]
    original_sections = [section.model_copy(deep=True) for section in sections]

    renderer.render(
        sections=sections,
        rendering_options=PromptContextRenderingOptions(),
        max_prompt_chars=400,
    )

    assert sections == original_sections


def test_prompt_builder_uses_system_instruction_builder_without_mutating_inputs():
    service = PromptBuilderService(
        system_instruction_builder=PromptContextSystemInstructionBuilder(
            application_rules=[
                "Use only provided context.",
                "Do not invent appointment data.",
            ]
        )
    )
    caller_instructions = [
        "Do not invent appointment data.",
        "Prefer deterministic summaries.",
    ]

    context = service.build_context(
        PromptBuildRequest(
            user_message="Help me book",
            system_instructions=caller_instructions,
        )
    )

    assert context.system_instructions.instructions == [
        "Use only provided context.",
        "Do not invent appointment data.",
        "Prefer deterministic summaries.",
    ]
    assert caller_instructions == [
        "Do not invent appointment data.",
        "Prefer deterministic summaries.",
    ]


def test_workflow_collector_returns_none_when_no_workflow_exists():
    collector = PromptContextWorkflowCollector()

    context = collector.collect(active_intent=None, conversation_state={})

    assert context is None


def test_knowledge_collector_returns_empty_collection_for_no_documents():
    collector = PromptContextKnowledgeCollector()

    context = collector.collect(documents=[], active_intent=None)

    assert context.knowledge_context is None
    assert context.included_document_ids == []
    assert context.excluded_document_ids == []
    assert context.requires_domain_validation is False


def test_conversation_collector_returns_none_for_empty_state():
    collector = PromptContextConversationCollector()

    context = collector.collect(user_message="Hello", conversation_state={})

    assert context is None


def test_prompt_builder_normalizes_single_turn_conversation_state():
    service = PromptBuilderService()

    context = service.build_context(
        PromptBuildRequest(
            user_message="I need help booking",
            conversation_state={
                "conversation_id": "conv-1",
                "history": [{"role": "user", "text": "I need help booking"}],
            },
        )
    )

    assert context.conversation_context is not None
    assert context.conversation_context.current_user_message == "I need help booking"
    assert context.conversation_context.previous_turns == []
    assert context.conversation_context.assistant_turns == []
    assert context.conversation_context.metadata == {"conversation_id": "conv-1"}


def test_prompt_builder_normalizes_multi_turn_conversation_state_deterministically():
    service = PromptBuilderService()
    conversation_state = {
        "conversation_id": "conv-2",
        "context": {"turn_count": 3, "last_intent": "BOOK_APPOINTMENT"},
        "metadata": {"source": "chat-api"},
        "history": [
            {"role": "user", "text": "I want to see a dermatologist"},
            {"role": "assistant", "text": "Do you have a preferred date?", "intent": "ASK_DATE"},
            {"role": "user", "text": "Tomorrow morning"},
        ],
    }

    first_context = service.build_context(
        PromptBuildRequest(
            user_message="Tomorrow morning",
            conversation_state=conversation_state,
        )
    )
    second_context = service.build_context(
        PromptBuildRequest(
            user_message="Tomorrow morning",
            conversation_state=conversation_state,
        )
    )

    assert first_context.conversation_context == second_context.conversation_context
    assert first_context.conversation_context is not None
    assert [turn.role for turn in first_context.conversation_context.previous_turns] == [
        "user",
        "assistant",
    ]
    assert [turn.message for turn in first_context.conversation_context.previous_turns] == [
        "I want to see a dermatologist",
        "Do you have a preferred date?",
    ]
    assert [turn.message for turn in first_context.conversation_context.assistant_turns] == [
        "Do you have a preferred date?"
    ]
    assert first_context.conversation_context.metadata == {
        "conversation_id": "conv-2",
        "context": {"turn_count": 3, "last_intent": "BOOK_APPOINTMENT"},
        "metadata": {"source": "chat-api"},
    }


def test_prompt_builder_renders_normalized_conversation_context_without_mutating_input():
    service = PromptBuilderService()
    conversation_state = {
        "conversation_id": "conv-3",
        "history": [
            {"role": "user", "text": "Find me a cardiologist"},
            {"role": "assistant", "text": "What day works for you?"},
        ],
    }

    result = service.build(
        PromptBuildRequest(
            user_message="Friday afternoon",
            conversation_state=conversation_state,
        )
    )

    assert '"current_user_message":"Friday afternoon"' in result.prompt
    assert '"previous_turns":[{"message":"Find me a cardiologist","metadata":{},"role":"user"}' in result.prompt
    assert '"assistant_turns":[{"message":"What day works for you?","metadata":{},"role":"assistant"}]' in result.prompt
    assert conversation_state == {
        "conversation_id": "conv-3",
        "history": [
            {"role": "user", "text": "Find me a cardiologist"},
            {"role": "assistant", "text": "What day works for you?"},
        ],
    }


def test_prompt_builder_normalizes_booking_workflow_from_nested_conversation_context():
    service = PromptBuilderService()
    conversation_state = {
        "conversation_id": "conv-4",
        "context": {
            "current_workflow": {
                "workflow_type": "BOOK_APPOINTMENT",
                "status": "INPUT_REQUIRED",
                "draft": {
                    "doctor_id": 1,
                    "doctor_name": "Dr. Sarah Jenkins",
                    "appointment_date": "2026-07-10",
                },
                "missing_fields": ["start_time", "patient_email"],
                "last_transition": "awaiting_patient_details",
            }
        },
    }

    context = service.build_context(
        PromptBuildRequest(
            user_message="Tomorrow at 10 AM",
            conversation_state=conversation_state,
            active_intent="BOOK_APPOINTMENT",
        )
    )

    assert context.workflow_context is not None
    assert context.workflow_context.active_intent == "BOOK_APPOINTMENT"
    assert context.workflow_context.workflow_status == "INPUT_REQUIRED"
    assert context.workflow_context.collected_fields == {
        "doctor_id": 1,
        "doctor_name": "Dr. Sarah Jenkins",
        "appointment_date": "2026-07-10",
    }
    assert context.workflow_context.missing_fields == ["start_time", "patient_email"]
    assert context.workflow_context.metadata == {
        "last_transition": "awaiting_patient_details"
    }
    assert context.workflow_context.state == {
        "workflow_type": "BOOK_APPOINTMENT",
        "status": "INPUT_REQUIRED",
        "draft": {
            "doctor_id": 1,
            "doctor_name": "Dr. Sarah Jenkins",
            "appointment_date": "2026-07-10",
        },
        "missing_fields": ["start_time", "patient_email"],
        "last_transition": "awaiting_patient_details",
    }


def test_prompt_builder_normalizes_legacy_cancellation_workflow_shape():
    service = PromptBuilderService()

    context = service.build_context(
        PromptBuildRequest(
            user_message="Cancel my appointment",
            conversation_state={
                "workflow": "CANCEL_APPOINTMENT",
                "status": "INPUT_REQUIRED",
                "missing": ["appointment_reference"],
                "source": "legacy",
            },
            active_intent="CANCEL_APPOINTMENT",
        )
    )

    assert context.workflow_context is not None
    assert context.workflow_context.active_intent == "CANCEL_APPOINTMENT"
    assert context.workflow_context.workflow_status == "INPUT_REQUIRED"
    assert context.workflow_context.collected_fields == {}
    assert context.workflow_context.missing_fields == ["appointment_reference"]
    assert context.workflow_context.metadata == {"source": "legacy"}


def test_prompt_builder_normalizes_completed_workflow_deterministically_without_mutation():
    service = PromptBuilderService()
    conversation_state = {
        "workflow_state": {
            "workflow_type": "APPOINTMENT_CONFIRMATION",
            "status": "COMPLETED",
            "draft": {
                "appointment_id": 42,
                "confirmation_code": "CN-12345-AB",
            },
            "missing_fields": [],
            "result_summary": "Appointment confirmed",
        }
    }

    first_context = service.build_context(
        PromptBuildRequest(
            user_message="Show my appointment",
            conversation_state=conversation_state,
            active_intent="APPOINTMENT_CONFIRMATION",
        )
    )
    second_context = service.build_context(
        PromptBuildRequest(
            user_message="Show my appointment",
            conversation_state=conversation_state,
            active_intent="APPOINTMENT_CONFIRMATION",
        )
    )

    assert first_context.workflow_context == second_context.workflow_context
    assert first_context.workflow_context is not None
    assert first_context.workflow_context.workflow_status == "COMPLETED"
    assert first_context.workflow_context.collected_fields == {
        "appointment_id": 42,
        "confirmation_code": "CN-12345-AB",
    }
    assert first_context.workflow_context.metadata == {
        "result_summary": "Appointment confirmed"
    }
    assert conversation_state == {
        "workflow_state": {
            "workflow_type": "APPOINTMENT_CONFIRMATION",
            "status": "COMPLETED",
            "draft": {
                "appointment_id": 42,
                "confirmation_code": "CN-12345-AB",
            },
            "missing_fields": [],
            "result_summary": "Appointment confirmed",
        }
    }


def test_prompt_builder_keeps_active_intent_only_workflow_context_for_backward_compatibility():
    service = PromptBuilderService()

    context = service.build_context(
        PromptBuildRequest(
            user_message="Help me book",
            active_intent="BOOK_APPOINTMENT",
        )
    )

    assert context.workflow_context is not None
    assert context.workflow_context.active_intent == "BOOK_APPOINTMENT"
    assert context.workflow_context.workflow_status is None
    assert context.workflow_context.collected_fields == {}
    assert context.workflow_context.missing_fields == []
    assert context.workflow_context.metadata == {}
    assert context.workflow_context.state == {}


def test_prompt_builder_normalizes_single_knowledge_document_metadata_and_hints():
    service = PromptBuilderService()
    document = _build_document(
        document_id="faq.policy",
        title="Booking Policy",
        summary="Policy summary.",
        content={"policy": "Bring ID"},
        include_when_intents=["BOOK_APPOINTMENT"],
        exclude_when_intents=["CANCEL_APPOINTMENT"],
        safe_to_quote=True,
        requires_domain_validation=True,
        max_context_chars=120,
        metadata={"locale": "en-IN", "revision": 3},
    )

    context = service.build_context(
        PromptBuildRequest(
            user_message="What should I bring?",
            active_intent="BOOK_APPOINTMENT",
            documents=[document],
        )
    )

    assert context.metadata.included_document_ids == ["faq.policy"]
    assert context.metadata.excluded_document_ids == []
    assert context.metadata.requires_domain_validation is True
    assert context.knowledge_context is not None
    assert context.knowledge_context.documents == [
        PromptContextKnowledgeDocument(
            document_id="faq.policy",
            title="Booking Policy",
            source_path="faq/faq.policy.md",
            domain="faq",
            audience="patient",
            summary="Policy summary.",
            content={"policy": "Bring ID"},
            include_when_intents=["BOOK_APPOINTMENT"],
            exclude_when_intents=["CANCEL_APPOINTMENT"],
            safe_to_quote=True,
            requires_domain_validation=True,
            max_context_chars=120,
            metadata={"locale": "en-IN", "revision": 3},
        )
    ]


def test_prompt_builder_normalizes_multiple_knowledge_documents_deterministically_without_mutation():
    service = PromptBuilderService()
    documents = [
        _build_document(
            document_id="faq.first",
            title="First Doc",
            content={"steps": ["one", "two"]},
            metadata={"rank": 1},
        ),
        _build_document(
            document_id="faq.second",
            title="Second Doc",
            content="Second content.",
            safe_to_quote=False,
            metadata={"rank": 2},
        ),
    ]

    first_context = service.build_context(
        PromptBuildRequest(
            user_message="Need help",
            documents=documents,
        )
    )
    second_context = service.build_context(
        PromptBuildRequest(
            user_message="Need help",
            documents=documents,
        )
    )

    assert first_context.knowledge_context == second_context.knowledge_context
    assert first_context.metadata.included_document_ids == ["faq.first", "faq.second"]
    assert first_context.knowledge_context is not None
    assert [
        document.document_id for document in first_context.knowledge_context.documents
    ] == ["faq.first", "faq.second"]
    assert documents[0].content == {"steps": ["one", "two"]}
    assert documents[0].metadata == {"rank": 1}
    assert documents[1].metadata == {"rank": 2}


def test_prompt_builder_knowledge_collector_tracks_include_and_exclude_deterministically():
    service = PromptBuilderService()
    allowed_document = _build_document(
        document_id="faq.allowed",
        include_when_intents=["BOOK_APPOINTMENT"],
    )
    excluded_document = _build_document(
        document_id="faq.excluded",
        exclude_when_intents=["BOOK_APPOINTMENT"],
    )
    unrelated_document = _build_document(
        document_id="faq.other-intent",
        include_when_intents=["CANCEL_APPOINTMENT"],
    )

    context = service.build_context(
        PromptBuildRequest(
            user_message="Help me book",
            active_intent="BOOK_APPOINTMENT",
            documents=[allowed_document, excluded_document, unrelated_document],
        )
    )

    assert context.metadata.included_document_ids == ["faq.allowed"]
    assert context.metadata.excluded_document_ids == [
        "faq.excluded",
        "faq.other-intent",
    ]
    assert context.knowledge_context is not None
    assert [document.document_id for document in context.knowledge_context.documents] == [
        "faq.allowed"
    ]


def test_prompt_builder_validates_a_valid_prompt_context():
    service = PromptBuilderService()
    context = service.build_context(
        PromptBuildRequest(
            user_message="Help me book",
            documents=[_build_document(document_id="faq.booking")],
        )
    )

    validation = service.validate_context(context)

    assert validation == PromptContextValidationResult(is_valid=True, issues=[])


def test_prompt_builder_validation_rejects_duplicate_knowledge_document_ids():
    service = PromptBuilderService()
    duplicate_document = PromptContextKnowledgeDocument(
        document_id="faq.booking",
        title="Booking Help",
        source_path="faq/booking.md",
        domain="faq",
        audience="patient",
        summary="Booking help summary.",
        content="Booking help content.",
        safe_to_quote=True,
    )
    context = PromptContext(
        metadata=PromptContextMetadata(
            included_document_ids=["faq.booking", "faq.booking"],
        ),
        user_context=PromptContextUserContext(message="Help me book"),
        knowledge_context=PromptContextKnowledgeContext(
            documents=[duplicate_document, duplicate_document]
        ),
    )

    validation = service.validate_context(context)

    assert validation.is_valid is False
    assert any(issue.code == "duplicate_document_ids" for issue in validation.issues)


def test_prompt_builder_validation_rejects_invalid_constraints():
    service = PromptBuilderService()
    context = PromptContext.model_construct(
        metadata=PromptContextMetadata(),
        user_context=PromptContextUserContext(message="Need help"),
        system_instructions=PromptContextSystemInstructions(),
        constraints=PromptContextConstraints.model_construct(max_prompt_chars=5),
        rendering_options=PromptContextRenderingOptions(),
    )

    validation = service.validate_context(context)

    assert validation.is_valid is False
    assert any(issue.code == "invalid_constraint" for issue in validation.issues)


def test_prompt_builder_validation_rejects_invalid_rendering_options():
    service = PromptBuilderService()
    context = PromptContext.model_construct(
        metadata=PromptContextMetadata(),
        user_context=PromptContextUserContext(message="Need help"),
        system_instructions=PromptContextSystemInstructions(),
        constraints=PromptContextConstraints(),
        rendering_options=PromptContextRenderingOptions.model_construct(
            include_section_headers=True,
            json_sort_keys=True,
            json_ensure_ascii=True,
            json_compact=True,
            truncation_marker="[TRUNCATED]\nMORE",
        ),
    )

    validation = service.validate_context(context)

    assert validation.is_valid is False
    assert any(issue.code == "invalid_rendering_option" for issue in validation.issues)


def test_prompt_builder_validation_rejects_inconsistent_workflow_metadata():
    service = PromptBuilderService()
    context = PromptContext(
        metadata=PromptContextMetadata(active_intent="BOOK_APPOINTMENT"),
        user_context=PromptContextUserContext(message="Need help"),
        workflow_context=PromptContextWorkflowContext(active_intent="CANCEL_APPOINTMENT"),
    )

    validation = service.validate_context(context)

    assert validation.is_valid is False
    assert any(issue.code == "inconsistent_workflow_metadata" for issue in validation.issues)


def test_prompt_builder_validation_rejects_invalid_workflow_missing_fields():
    service = PromptBuilderService()
    context = PromptContext.model_construct(
        metadata=PromptContextMetadata(active_intent="BOOK_APPOINTMENT"),
        user_context=PromptContextUserContext(message="Need help"),
        workflow_context=PromptContextWorkflowContext.model_construct(
            active_intent="BOOK_APPOINTMENT",
            missing_fields=["patient_email", ""],
        ),
        system_instructions=PromptContextSystemInstructions(),
        constraints=PromptContextConstraints(),
        rendering_options=PromptContextRenderingOptions(),
    )

    validation = service.validate_context(context)

    assert validation.is_valid is False
    assert any(issue.code == "invalid_workflow_metadata" for issue in validation.issues)


def test_prompt_builder_applies_prompt_hints_as_constraints():
    service = PromptBuilderService()
    included_document = _build_document(
        document_id="faq.allowed",
        include_when_intents=["BOOK_APPOINTMENT"],
        requires_domain_validation=True,
        safe_to_quote=False,
    )
    excluded_document = _build_document(
        document_id="faq.excluded",
        exclude_when_intents=["BOOK_APPOINTMENT"],
    )

    result = service.build(
        PromptBuildRequest(
            user_message="Can I book for tomorrow?",
            active_intent="BOOK_APPOINTMENT",
            documents=[included_document, excluded_document],
        )
    )

    assert result.included_document_ids == ["faq.allowed"]
    assert result.excluded_document_ids == ["faq.excluded"]
    assert result.requires_domain_validation is True
    assert "Quoted content omitted because the document is not marked safe_to_quote." in result.prompt
    assert "faq.excluded" not in result.prompt


def test_prompt_builder_pipeline_preserves_renderer_compatibility_and_block_contract():
    service = PromptBuilderService()

    result = service.build(
        PromptBuildRequest(
            user_message="Need help",
            conversation_state={"history": [{"role": "assistant", "text": "How can I help?"}]},
            system_instructions=["Use only provided context."],
        )
    )

    assert result.blocks[0].kind.value == "user_message"
    assert result.blocks[1].kind.value == "conversation_state"
    assert result.blocks[0].label == "User Message"
    assert result.blocks[1].label == "Conversation State"
    assert "[System Instructions]" in result.prompt
    assert "[User Message]" in result.prompt
    assert "[Conversation State]" in result.prompt


def test_prompt_builder_raises_deterministic_validation_error_before_rendering():
    class InvalidContextPromptBuilderService(PromptBuilderService):
        def build_context(self, request: PromptBuildRequest) -> PromptContext:
            return PromptContext.model_construct(
                metadata=PromptContextMetadata(),
                user_context=PromptContextUserContext.model_construct(message=" "),
                system_instructions=PromptContextSystemInstructions(),
                constraints=PromptContextConstraints(),
                rendering_options=PromptContextRenderingOptions(),
            )

    service = InvalidContextPromptBuilderService()

    try:
        service.build(PromptBuildRequest(user_message="Ignored by override"))
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected validation error")

    assert message.startswith("PromptContext validation failed:")
    assert '"code": "empty_user_message"' in message


def test_prompt_builder_enforces_document_and_total_prompt_budgets():
    service = PromptBuilderService()
    document = _build_document(
        document_id="faq.long",
        summary="Long document summary.",
        content="A" * 200,
        max_context_chars=40,
    )

    clipped_result = service.build(
        PromptBuildRequest(
            user_message="Summarize the policy",
            documents=[document],
            max_prompt_chars=400,
        )
    )
    truncated_result = service.build(
        PromptBuildRequest(
            user_message="Summarize the policy",
            documents=[document],
            max_prompt_chars=180,
        )
    )

    assert clipped_result.truncated is False
    assert "A" * 60 not in clipped_result.prompt
    assert "A" * 40 in clipped_result.prompt
    assert truncated_result.truncated is True
    assert "[TRUNCATED]" in truncated_result.prompt
