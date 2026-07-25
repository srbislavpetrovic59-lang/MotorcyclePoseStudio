#include "PoseWebSocketComponent.h"

#include "WebSocketsModule.h"
#include "Modules/ModuleManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"


UPoseWebSocketComponent::UPoseWebSocketComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}


void UPoseWebSocketComponent::BeginPlay()
{
    Super::BeginPlay();

    Connect();
}


void UPoseWebSocketComponent::Connect()
{
    FModuleManager::LoadModuleChecked<FWebSocketsModule>("WebSockets");

    WebSocket = FWebSocketsModule::Get().CreateWebSocket(
        TEXT("ws://127.0.0.1:8765")
    );

    WebSocket->OnConnected().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleConnected
    );

    WebSocket->OnConnectionError().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleConnectionError
    );

    WebSocket->OnClosed().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleClosed
    );

    WebSocket->OnMessage().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleMessage
    );

    UE_LOG(
        LogTemp,
        Display,
        TEXT("Pose WebSocket: connecting to ws://127.0.0.1:8765")
    );

    WebSocket->Connect();
}


void UPoseWebSocketComponent::HandleConnected()
{
    UE_LOG(
        LogTemp,
        Display,
        TEXT("Pose WebSocket: connected")
    );
}


void UPoseWebSocketComponent::HandleConnectionError(
    const FString& Error
)
{
    UE_LOG(
        LogTemp,
        Error,
        TEXT("Pose WebSocket connection error: %s"),
        *Error
    );
}


void UPoseWebSocketComponent::HandleClosed(
    int32 StatusCode,
    const FString& Reason,
    bool bWasClean
)
{
    if (StatusCode == 1000)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Pose WebSocket closed normally.")
        );
        return;
    }

    UE_LOG(
        LogTemp,
        Warning,
        TEXT(
            "Pose WebSocket closed. Code: %d, Reason: %s"
        ),
        StatusCode,
        *Reason
    );
}


void UPoseWebSocketComponent::HandleMessage(
    const FString& Message
)
{
    UE_LOG(
        LogTemp,
        Display,
        TEXT("Pose WebSocket received: %s"),
        *Message
    );

    TSharedPtr<FJsonObject> JsonObject;

    TSharedRef<TJsonReader<>> Reader =
        TJsonReaderFactory<>::Create(Message);

    if (!FJsonSerializer::Deserialize(Reader, JsonObject) ||
        !JsonObject.IsValid())
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("Invalid JSON received.")
        );
        return;
    }

    double LeftElbow = 0.0;
    double RightElbow = 0.0;
    float LeftKnee = 0.0f;
    float RightKnee = 0.0f;
    float TorsoAngle = 0.0f;
    float PoseConfidence = 0.0f ;

    if (JsonObject->TryGetNumberField(
        TEXT("left_elbow"),
        LeftElbow))
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Left elbow = %.1f"),
            LeftElbow
        );
    }
    if (JsonObject->TryGetNumberField(
        TEXT("right_elbow"),
        LeftElbow))
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Right elbow = %.1f"),
            RightElbow
        );
    }
    if (JsonObject->TryGetNumberField(
        TEXT("left_knee"),
        LeftKnee))
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Left knee = %.1f"),
            LeftKnee
        );
    }
    if (JsonObject->TryGetNumberField(
        TEXT("right_knee"),
        RightKnee))
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Right knee = %.1f"),
            RightKnee
        );
    }
    if (JsonObject->TryGetNumberField(
        TEXT("torso_angle"),
        TorsoAngle))
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Torso angle = %.1f"),
            TorsoAngle
        );
    }
    if (JsonObject->TryGetNumberField(
        TEXT("pose_confidence"),
        PoseConfidence))
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Pose confidence = %.1f"),
            PoseConfidence
        );
    }
}

void UPoseWebSocketComponent::TickComponent(
    float DeltaTime,
    ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction
)
{
    Super::TickComponent(
        DeltaTime,
        TickType,
        ThisTickFunction
    );
}